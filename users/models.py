from django.db import models
from pathlib import PurePath
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from imagekit.models import ProcessedImageField
from imagekit.processors import SmartResize

from .enums import ProfileVisibilityEnums

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom User class implementing a fully featured User model with
    admin-compliant permissions.
    Email, username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()
    email_validator = EmailValidator()

    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Format: example@mail.com'),
        validators=[email_validator],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_('first name'), max_length=75, blank=True)
    last_name = models.CharField(_('last name'), max_length=75, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


def profile_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format('profile-image', ext)
    return PurePath('profiles', instance.user.username, filename)

def profile_cover_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format('profile-cover-image', ext)
    return PurePath('profiles', instance.user.username, filename)
class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    bio = models.CharField(_('bio'), max_length=150, blank=True)
    visibility = models.IntegerField(choices=ProfileVisibilityEnums.choices, default=ProfileVisibilityEnums.PUBLIC)
    points = models.IntegerField(default=0, verbose_name="Total points achieved by user")
    
    image = ProcessedImageField(
        upload_to=profile_image_upload_path, 
        blank=True, 
        help_text="Profile Picture",
        verbose_name="Profile Picture",
        processors=[SmartResize(300, 300)],
        format='JPEG',
        options={'quality': 85},
    )

    cover_image = ProcessedImageField(
        upload_to=profile_cover_image_upload_path, 
        blank=True, 
        help_text="Profile Cover Picture",
        verbose_name="Profile Cover Picture",
        format='JPEG',
        options={'quality': 85},
    )

    @classmethod
    def add_following(cls, user, following):
        user = cls.objects.get(user=user)
        following = cls.objects.get(user=following)
        UserFollows.objects.get_or_create(user_profile=user, following_user_profile=following)

    @classmethod
    def remove_following(cls, user, following):
        user = cls.objects.get(user=user)
        following = cls.objects.get(user=following)
        UserFollows.objects.get(user_profile=user, following_user_profile=following).delete()


    def __str__(self):
        return f'Profile: {str(self.user)}'
        
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

class UserFollows(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following")
    following_user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="followers")
    followed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.user_profile.user)} -> {str(self.following_user_profile.user)}'

    class Meta:
        verbose_name = 'User Follows'
        verbose_name_plural = 'User Follows'
        unique_together = ['user_profile', 'following_user_profile']

