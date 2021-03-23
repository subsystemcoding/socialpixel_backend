from django.contrib import admin
from .models import Channel, Game, Leaderboard, LeaderboardRow

admin.site.register(Channel)
admin.site.register(Game)
admin.site.register(Leaderboard)
admin.site.register(LeaderboardRow)

