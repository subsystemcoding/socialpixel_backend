from uuid import uuid4
from django.utils import timezone
from django.db import models
from users.models import Profile
from posts.models import Post
from pathlib import PurePath
from upload_validator import FileTypeValidator
from django.core.validators import FileExtensionValidator


class ChatRoom(models.Model):
    created_by = models.ForeignKey(Profile, related_name='created_by', on_delete=models.CASCADE)
    name = models.TextField()
    id = models.BigAutoField(primary_key=True)
    members = models.ManyToManyField(Profile, related_name='member_in',blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_messaged_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.name)

class Message(models.Model):
    author = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,
        related_name='messaged_by',
    )
    id = models.BigAutoField(primary_key=True)
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
