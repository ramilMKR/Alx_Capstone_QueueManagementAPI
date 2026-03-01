from rest_framework import serializers
from .models import ServiceQueue, QueueEntry

class ServiceQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceQueue
        fields = '__all__'

class QueueEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = QueueEntry
        fields = ['id', 'queue', 'user', 'username', 'position', 'status', 'created_at']
        read_only_fields = ['position', 'status', 'created_at', 'username']