from django.contrib import admin
from .models import Match, MatchEvent, Team, TeamRequest, User, Player, PlayerInvite

admin.site.register(Match)
admin.site.register(MatchEvent)
admin.site.register(Team)
admin.site.register(TeamRequest)
admin.site.register(User)
admin.site.register(Player)
admin.site.register( PlayerInvite)
