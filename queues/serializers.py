from rest_framework import serializers
from .models import ServiceQueue, QueueEntry

class ServiceQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceQueue
        fields = '__all__'

class QueueEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueEntry
        fields = '__all__'