from pathlib import PurePath, Path
from django.db.models.signals import post_save
from .models import User, Profile
from django.dispatch import receiver
from PIL import Image
import os

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Profile)
def image_to_png(sender, instance, **kwargs):
    if instance.image:
        profile_image_dimension = 200
        file_ext = PurePath(instance.image.path).suffix
        if file_ext != ".png":
            im = Image.open(instance.image.path)

            if im.height > profile_image_dimension or im.width > profile_image_dimension:
                output_size = (profile_image_dimension, profile_image_dimension)
                im.thumbnail(output_size)
            old_path = instance.image.path
            im.save(instance.image.path.replace(file_ext, ".png"))
            instance.image = str(instance.image).replace(file_ext, ".png")
            instance.save()
            os.remove(old_path)

        img = Image.open(instance.image.path)
        if img.height > profile_image_dimension or img.width > profile_image_dimension:
            output_size = (profile_image_dimension, profile_image_dimension)
            img.thumbnail(output_size)
            img.save(instance.image.path)
