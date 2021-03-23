from django.db.models.signals import post_save
from .models import ChatRoom, Message
from django.dispatch import receiver


@receiver(post_save, sender=Message)
def update_last_messaged_timestamp(sender, instance, **kwargs):
    chatroom = ChatRoom.objects.get(id = instance.room.id)
    chatroom.last_messaged_timestamp = instance.timestamp
    chatroom.save()

    