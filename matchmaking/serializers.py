
from rest_framework import serializers
from .models import Team, Match, Player, ScoreProposition, PlayerInvite, TeamRequest


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'is_public', 'score']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'status', 'created_at', 'expires_at', 'inviting_team', 'guest_team', 'inviting_score', 'guest_score']

class ScorePropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreProposition
        fields = ['id', 'inviting_score', 'guest_score', 'suggesting_team', 'note', 'created_at']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'user', 'team']

class PlayerInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerInvite
        fields = ['id', 'expire_date', 'player', 'team']

class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = ['id', 'expire_date', 'player', 'team']
