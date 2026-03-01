from celery import shared_task
from django.core.mail import send_mail

@shared_task
def notify_user_turn(email, queue_name):
    send_mail(
        subject=f"Your turn in {queue_name}!",
        message="It's your turn in the queue. Please proceed.",
        from_email="no-reply@queueapi.com",
        recipient_list=[email],
        fail_silently=False,
    )