# Generated by Django 3.1.7 on 2021-03-26 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20210323_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
