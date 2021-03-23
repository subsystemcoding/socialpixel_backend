from django.db import models
from pathlib import PurePath
from uuid import uuid4
from users.models import Profile
from posts.models import Post
from upload_validator import FileTypeValidator
from django.core.validators import FileExtensionValidator

class Channel(models.Model):

    def coverimage_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('channelCoverImages', filename)

    def avatar_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('channelAvatars', filename)

    image_file_validator = FileTypeValidator(
        allowed_types=['image/png', 'image/jpeg', 'image/bmp',
            'image/heic', 'image/heif', 'image/tiff', 'image/gif'],
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    subscribers = models.ManyToManyField(
        Profile, related_name='subscribed', blank=True)
    cover_image = models.ImageField(
        upload_to=coverimage_upload_path,
        help_text="Cover Image",
        verbose_name="Cover Image",
        validators=[image_file_validator, FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
        # max_upload_size=52428800,
        blank=True
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        help_text="Channel Avatar",
        verbose_name="Channel Avatar",
        validators=[image_file_validator, FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
        # max_upload_size=52428800,
        blank=True
    )

    def __str__(self):
        return str(self.id) + ':' + str(self.name)

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'

class Leaderboard(models.Model):
    id = models.BigAutoField(primary_key=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Leaderboard'
        verbose_name_plural = 'Leaderboards'

class LeaderboardRow(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    points = models.IntegerField()
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + ":" + str(self.user)
    class Meta:
        verbose_name = 'LeaderboardRow'
        verbose_name_plural = 'LeaderboardRows'

class Game(models.Model):

    def gameimage_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        post = f'{instance.author}:{uuid4()}'
        filename = '{}.{}'.format(post, ext)
        return PurePath('gameImages', filename)

    image_file_validator = FileTypeValidator(
        allowed_types=['image/png', 'image/jpeg', 'image/bmp', 'image/heic', 'image/heif', 'image/tiff', 'image/gif'],
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to=gameimage_upload_path,
        help_text="Game Image",
        verbose_name="Game Image",
        validators=[image_file_validator, FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])],
        # max_upload_size=52428800,
        blank=True
    )

    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, blank=True)
    posts = models.ManyToManyField(Post, related_name="in_game", blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    pinColorHex = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return str(self.id) + ':' + str(self.name)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
