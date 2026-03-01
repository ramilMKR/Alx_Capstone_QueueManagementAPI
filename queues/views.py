from django.shortcuts import render
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ServiceQueue, QueueEntry
from .serializers import ServiceQueueSerializer, QueueEntrySerializer
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .tasks import notify_user_turn

# List all queues
class QueueListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queues = ServiceQueue.objects.all()
        serializer = ServiceQueueSerializer(queues, many=True)
        return Response(serializer.data)


# Create queue (admin only)
class QueueCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins can create queues"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ServiceQueueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Join queue
class JoinQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, queue_id):
        queue = get_object_or_404(ServiceQueue, id=queue_id)
        # Check if queue is active
        if not queue.is_active:
            return Response({"error": "This queue is not active"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent user from joining the same queue multiple times
        if QueueEntry.objects.filter(queue=queue, user=request.user, status='waiting').exists():
            return Response({"error": "You are already in this queue"}, status=status.HTTP_400_BAD_REQUEST)

        # Determine next position (must be >= 1)
        last_position = QueueEntry.objects.filter(queue=queue).aggregate(Max('position'))['position__max'] or 0
        next_position = last_position + 1
        if next_position < 1:
            next_position = 1  # Safety check

        # Create queue entry
        entry = QueueEntry.objects.create(queue=queue, user=request.user, position=next_position)
        serializer = QueueEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# Leave queue
class LeaveQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, queue_id):
        queue = get_object_or_404(ServiceQueue, id=queue_id)
        entry = QueueEntry.objects.filter(queue=queue, user=request.user, status='waiting').first()
        if not entry:
            return Response({"error": "You are not in this queue"}, status=status.HTTP_400_BAD_REQUEST)
        entry.status = 'left'
        entry.save()
        return Response({"message": "Left the queue"})


# Get my position
class MyPositionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = QueueEntry.objects.filter(user=request.user, status='waiting')
        serializer = QueueEntrySerializer(entries, many=True)
        return Response(serializer.data)


# Admin: mark next in queue as served
class NextInQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, queue_id):
        queue = get_object_or_404(ServiceQueue, id=queue_id)

        # Get the next waiting user (lowest position)
        next_entry = QueueEntry.objects.filter(queue=queue, status='waiting').order_by('position').first()
        if not next_entry:
            return Response({"error": "No users waiting in this queue."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark current user as served
        next_entry.status = 'served'
        next_entry.save()

        # Update positions for remaining users
        remaining_entries = QueueEntry.objects.filter(queue=queue, status='waiting').order_by('position')
        for idx, entry in enumerate(remaining_entries, start=1):
            entry.position = idx
            entry.save()

        # Real-time update via Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'queue_{queue.id}',
            {
                'type': 'queue_update',
                'data': {
                    'message': f'{next_entry.user.username} is now being served',
                    'queue_id': queue.id,
                    'served_user': next_entry.user.username,
                    'next_positions': [
                        {'user': e.user.username, 'position': e.position} for e in remaining_entries
                    ]
                }
            }
        )

        # Send notification to the served user
        notify_user_turn.delay(next_entry.user.email, queue.name)

        serializer = QueueEntrySerializer(next_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)