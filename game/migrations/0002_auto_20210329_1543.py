# Generated by Django 3.1.7 on 2021-03-29 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0001_initial'),
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='validatepost',
            name='creator_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_post', to='posts.post'),
        ),
        migrations.AddField(
            model_name='validatepost',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.game'),
        ),
        migrations.AddField(
            model_name='validatepost',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='posts.post'),
        ),
        migrations.AddField(
            model_name='leaderboardrow',
            name='leaderboard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.leaderboard'),
        ),
    ]
