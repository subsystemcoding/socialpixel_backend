# Generated by Django 3.1.7 on 2021-03-29 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0002_auto_20210329_0834'),
        ('tags', '0001_initial'),
        ('users', '0001_initial'),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboardrow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
        ),
        migrations.AddField(
            model_name='game',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.channel'),
        ),
        migrations.AddField(
            model_name='game',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
        ),
        migrations.AddField(
            model_name='game',
            name='leaderboard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.leaderboard'),
        ),
        migrations.AddField(
            model_name='game',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='in_game', to='posts.Post'),
        ),
        migrations.AddField(
            model_name='game',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tagged_game', to='tags.Tag'),
        ),
        migrations.AddField(
            model_name='channel',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscribed', to='users.Profile'),
        ),
        migrations.AddField(
            model_name='channel',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tagged_channel', to='tags.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='validatepost',
            unique_together={('game', 'post')},
        ),
        migrations.AlterUniqueTogether(
            name='game',
            unique_together={('name', 'channel')},
        ),
    ]
