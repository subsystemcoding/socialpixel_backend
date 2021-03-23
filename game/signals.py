from django.db.models.signals import post_save
from .models import Leaderboard, Game
from django.dispatch import receiver


@receiver(post_save, sender=Game)
def create_leaderboard_for_new_game(sender, instance, created, **kwargs):
    if created:
        leaderboard = Leaderboard()
        leaderboard.save()
        game = Game.objects.get(id=instance.id)
        game.leaderboard = leaderboard
        game.save()
