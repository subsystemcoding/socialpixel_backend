from django.db import models
from pathlib import PurePath
from uuid import uuid4

from users.models import Profile
from tags.models import Tag
from imagekit.models.fields import ImageSpecField
from imagekit.processors.resize import ResizeToFill

from upload_validator import FileTypeValidator
from django.core.validators import FileExtensionValidator

from .enums import PostVisibilityEnums

class Post(models.Model):

    def imagepost_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('imageposts', filename)

    image_file_validator = FileTypeValidator(
        allowed_types=['image/png', 'image/jpeg', 'image/bmp',
                       'image/heic', 'image/heif', 'image/tiff', 'image/gif'],
    )

    post_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='posted_by',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=256, blank=True)
    gps_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)
    gps_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True)
    tagged_users = models.ManyToManyField(
        Profile,
        related_name='tagged',
        blank=True
    )
    upvotes = models.ManyToManyField(
        Profile, related_name='upvoted_by', blank=True)
    views = models.PositiveIntegerField(default=0)
    visibility = models.IntegerField(
        choices=PostVisibilityEnums.choices, default=PostVisibilityEnums.ACTIVE)
    tags = models.ManyToManyField(Tag, related_name="tagged_post", blank=True)
    channel = models.ForeignKey('game.Channel', on_delete=models.SET_NULL, null=True, blank=True)

    image = models.ImageField(
        upload_to=imagepost_upload_path,
        help_text="Post Image",
        verbose_name="Post Image",
        validators=[image_file_validator, FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
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
        return str(self.author.user) + ':' + str(self.post_id)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    post_id = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='commented_by')
    comment_content = models.CharField(max_length=256)
    reply_to_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.post_id) + ':' + str(self.author.user) + ':' + str(self.comment_id)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
