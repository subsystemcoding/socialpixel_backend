from django.contrib import admin
from .models import Channel, Game, Leaderboard, LeaderboardRow, ReportedPost, ValidatePost

admin.site.register(Channel)
admin.site.register(Game)
admin.site.register(Leaderboard)
admin.site.register(LeaderboardRow)
admin.site.register(ValidatePost)
admin.site.register(ReportedPost)
