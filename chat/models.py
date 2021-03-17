from uuid import uuid4
from django.db import models
from django.conf import settings
from posts.models import Post
from pathlib import PurePath
from upload_validator import FileTypeValidator
from django.core.validators import FileExtensionValidator


class ChatRoom(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by', on_delete=models.CASCADE)
    uuid = models.UUIDField(default = uuid4, editable = False) 
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_in',)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.uuid)

class Message(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(default = uuid4, editable = False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)

    def imagepost_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('imagemessages', filename)

    image_file_validator = FileTypeValidator(
        allowed_types=['image/png', 'image/jpeg', 'image/bmp', 'image/heic', 'image/heif', 'image/tiff', 'image/gif'],
    )

    image = models.ImageField(
        upload_to=imagepost_upload_path,
        help_text="Post Image",
        verbose_name="Post Image",
        validators=[image_file_validator, FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
        # max_upload_size=52428800,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return "{}:{}".format(str(self.author), self.room)
