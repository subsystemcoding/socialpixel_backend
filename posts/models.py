from django.db import models
from django.conf import settings
from django.utils import timezone
from pathlib import PurePath
from uuid import uuid4

from imagekit.models.fields import ImageSpecField
from imagekit.processors.resize import ResizeToFill

from upload_validator import FileTypeValidator
from django.core.validators import FileExtensionValidator

class Post(models.Model):
    
    class VisibilityEnums(models.IntegerChoices):
        VISIBLE = 0
        HIDDEN = 1

    def imagepost_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('imageposts', filename)

    image_file_validator = FileTypeValidator(
        allowed_types=['image/png', 'image/jpeg', 'image/bmp', 'image/heic', 'image/heif', 'image/tiff', 'image/gif'],
    )

    post_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='posted_by',
    )
    date_created = models.DateTimeField(default=timezone.now)
    caption = models.CharField(max_length=256, blank=True)
    gps_tag = models.CharField(max_length=128, blank=True) # TODO: Update this later on to support GEOLOCATION
    tagged_users =  models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='tagged', 
        blank=True
    )
    upvotes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    visibility = models.IntegerField(choices=VisibilityEnums.choices, default=VisibilityEnums.VISIBLE)

    image = models.ImageField(
        upload_to=imagepost_upload_path,
        help_text="Post Image",
        verbose_name="Post Image",
        validators=[image_file_validator, FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
        # max_upload_size=52428800,
    )

    image_300x300 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90},
    )
    image_250x250 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(250, 250)],
        format='JPEG',
        options={'quality': 85},
    )
    image_200x200 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 85},
    )
    image_150x150 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 85},
    )
    image_100x100 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(100, 100)],
        format='JPEG',
        options={'quality': 85},
    )
    image_75x75 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(75, 75)],
        format='JPEG',
        options={'quality': 60},
    )

    def __str__(self):
        return str(self.author) + ':' + str(self.post_id)


class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    post_id = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='commented_on'
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commented_by')
    comment_content = models.CharField(max_length=256)
    reply_to_comment = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='replies'
    )
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.post_id) + ':' + str(self.author) + ':' + str(self.comment_id)