from os import name
from django.db.models.signals import post_save
from .models import Channel, Leaderboard, Game, LeaderboardRow
from django.dispatch import receiver
import random
from .schema import post_added_to_game
from users.models import Profile, User

@receiver(post_save, sender=Game)
def create_leaderboard_for_new_game(sender, instance, created, **kwargs):
    if created:
        leaderboard = Leaderboard()
        leaderboard.save()
        game = Game.objects.get(id=instance.id)
        game.leaderboard = leaderboard
        game.save()
        color = "%06x"%random.randint(0,0xFFFFFF)
        while Game.objects.all().values('pinColorHex').filter(pinColorHex=color).exists():
            color = "%06x"%random.randint(0,0xFFFFFF)
        game.pinColorHex = color
        game.save()


@receiver(post_added_to_game)
def calculate_leaderboard(sender, post_author, gamename, channelname, **kwargs):
    channel = Channel.objects.get(name=channelname)
    game = Game.objects.get(name=gamename, channel=channel)
    profile = Profile.objects.get(user=User.objects.get(username=post_author))
    game_creator = Profile.objects.get(user=User.objects.get(username=game.creator.user.username))
    leaderboard = game.leaderboard

    author_post_count = game.posts.filter(author=profile).count()
    game_creator_post_count = game.posts.filter(author=game_creator).count()

    leaderboard_row_count = leaderboard.leaderboardrow_set.count()

    if author_post_count == game_creator_post_count:
        points = 100
        if leaderboard_row_count == 0:
            points = 1000
        elif leaderboard_row_count == 1:
            points = 800
        elif leaderboard_row_count == 2:
            points = 600
        elif leaderboard_row_count == 3:
            points = 400
        elif leaderboard_row_count == 4:
            points = 200
        else:
            points = 100
        
        row = LeaderboardRow(leaderboard=leaderboard, user=profile, points=points)
        row.save()
        profile.points = profile.points + points
        profile.save()
