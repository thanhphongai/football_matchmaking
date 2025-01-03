
from rest_framework import serializers
from .models import Team, Match, Player, ScoreProposition, PlayerInvite, TeamRequest, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'mail']

class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.mail', read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'team']


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True) 
    class Meta:
        model = Team
        fields = ['id', 'name', 'is_public', 'score', 'players']

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'status', 'created_at', 'expires_at', 'inviting_team', 'guest_team', 'inviting_score', 'guest_score']

class ScorePropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreProposition
        fields = ['id', 'inviting_score', 'guest_score', 'suggesting_team', 'note', 'created_at']


class PlayerInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerInvite
        fields = ['id', 'expire_date', 'player', 'team']

class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = ['id', 'expire_date', 'player', 'team']
