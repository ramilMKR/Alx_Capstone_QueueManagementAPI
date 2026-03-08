from rest_framework import serializers
from .models import ServiceQueue, QueueEntry, Queue

class QueueEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = QueueEntry
        fields = ['id', 'queue', 'user', 'username', 'position', 'status', 'created_at']
        read_only_fields = ['position', 'status', 'created_at', 'username']

class ServiceQueueSerializer(serializers.ModelSerializer):
    entries = QueueEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceQueue
        fields = '__all__'
        fields = ["id", "name", "description", "is_active", "entries"]
