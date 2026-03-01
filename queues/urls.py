from django.urls import path
from .views import (
    QueueListView, QueueCreateView,
    JoinQueueView, LeaveQueueView,
    MyPositionView, NextInQueueView
)

urlpatterns = [
    path('queues/', QueueListView.as_view(), name='queue-list'),
    path('queues/create/', QueueCreateView.as_view(), name='queue-create'),
    path('queues/<int:queue_id>/join/', JoinQueueView.as_view(), name='queue-join'),
    path('queues/<int:queue_id>/leave/', LeaveQueueView.as_view(), name='queue-leave'),
    path('my-position/', MyPositionView.as_view(), name='my-position'),
    path('queues/<int:queue_id>/next/', NextInQueueView.as_view(), name='queue-next'),
]