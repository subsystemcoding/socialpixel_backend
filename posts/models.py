from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

class Post(models.Model):
    
    class VisibilityEnums(models.IntegerChoices):
        VISIBLE = 0
        HIDDEN = 1

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
    media_id = models.UUIDField() # For multiple media use : ArrayField(models.UUIDField())

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