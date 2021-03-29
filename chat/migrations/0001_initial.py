# Generated by Django 3.1.7 on 2021-03-28 11:51

import chat.models
import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import upload_validator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('name', models.CharField(max_length=256)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_messaged_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, help_text='Chat Image', null=True, upload_to=chat.models.Message.chatimage_upload_path, validators=[upload_validator.FileTypeValidator(allowed_types=['image/png', 'image/jpeg', 'image/bmp', 'image/heic', 'image/heif', 'image/tiff', 'image/gif']), django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'bmp', 'heic', 'heif', 'tiff', 'gif'])], verbose_name='Chat Image')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
