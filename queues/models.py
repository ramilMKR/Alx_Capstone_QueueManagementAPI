from django.db import models

# Create your models here.
from django.db import models
from django.forms import ValidationError
from accounts.models import User

class ServiceQueue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class QueueEntry(models.Model):
    STATUS_CHOICES = [('waiting','Waiting'),('served','Served'),('left','Left')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    queue = models.ForeignKey(ServiceQueue, on_delete=models.CASCADE, related_name='entries')
    position = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    joined_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.position < 1:
            raise ValidationError("Queue position cannot be less than 1.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['position']