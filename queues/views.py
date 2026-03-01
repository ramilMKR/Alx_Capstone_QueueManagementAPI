from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ServiceQueue, QueueEntry
from .serializers import ServiceQueueSerializer, QueueEntrySerializer
from django.shortcuts import get_object_or_404
from django.db.models import Max

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
        # Check if user already in queue
        if QueueEntry.objects.filter(queue=queue, user=request.user, status='waiting').exists():
            return Response({"error": "Already in queue"}, status=status.HTTP_400_BAD_REQUEST)
        # Determine next position
        last_position = QueueEntry.objects.filter(queue=queue).aggregate(Max('position'))['position__max'] or 0
        entry = QueueEntry.objects.create(queue=queue, user=request.user, position=last_position+1)
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
        if not request.user.is_staff:
            return Response({"error": "Only admins can serve next"}, status=status.HTTP_403_FORBIDDEN)
        queue = get_object_or_404(ServiceQueue, id=queue_id)
        next_entry = QueueEntry.objects.filter(queue=queue, status='waiting').order_by('position').first()
        if not next_entry:
            return Response({"message": "Queue is empty"})
        next_entry.status = 'served'
        next_entry.save()
        return Response({"message": f"User {next_entry.user.username} served"})