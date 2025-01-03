# matchmaking/views.py
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Team, Match, Player, PlayerInvite, TeamRequest, User
from .serializers import TeamSerializer, MatchSerializer, ScorePropositionSerializer, PlayerSerializer, TeamRequestSerializer, PlayerInviteSerializer

# Chi tiết đội bóng
class TeamDetailView(APIView):
    def get(self, request, id):
        try:
            team = Team.objects.get(id=id)
            serializer = TeamSerializer(team)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

class TeamListView(APIView):
    def get(self, request):
        try:
            team = Team.objects.all()
            serializer = TeamSerializer(team, many=True)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

# Thách đấu đội khác
class TeamChallengeAPIView(APIView):
    def post(self, request, id):
        try:
            inviting_team = Team.objects.get(id=id)
            guest_team_id = request.data.get('guest_team_id')
            guest_team = Team.objects.get(id=guest_team_id)

            match = Match.objects.create(
                inviting_team=inviting_team,
                guest_team=guest_team,
                status='PENDING',
                created_at=request.data.get('created_at'),
                expires_at=request.data.get('expires_at')
            )
            serializer = MatchSerializer(match)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
        

# Chi tiết trận đấu
class MatchDetailAPIView(APIView):
    def get(self, request, id):
        try:
            match = Match.objects.get(id=id)
            serializer = MatchSerializer(match)
            return Response(serializer.data)
        except Match.DoesNotExist:
            return Response({"detail": "Match not found."}, status=status.HTTP_404_NOT_FOUND)
        

# Đề xuất điểm số trận đấu
class MatchScorePropositionAPIView(APIView):
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            my_team_id = request.data.get('my_team_id')
            my_score = request.data.get('my_score')
            opponent_score = request.data.get('opponent_score')

            my_team = match.inviting_team if my_team_id == match.inviting_team.id else match.guest_team

            match.update_proposition(my_team, my_score, opponent_score)
            return Response({"detail": "Score proposition updated successfully."}, status=status.HTTP_200_OK)
        except Match.DoesNotExist:
            return Response({"detail": "Match not found."}, status=status.HTTP_404_NOT_FOUND)

# Tạo người chơi mới
class CreatePlayerAPIView(APIView):
    def post(self, request):
        user_data = request.data
        user = User.objects.create(
            name=user_data['name'],
            surname=user_data['surname'],
            mail=user_data['mail']
        )
        player = Player.objects.create(user=user)
        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Tạo đội bóng mới
class CreateTeamAPIView(APIView):
    def post(self, request):
        team_data = request.data
        team = Team.objects.create(
            name=team_data['name'],
            is_public=team_data['is_public']
        )
        serializer = TeamSerializer(team)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Mời người chơi tham gia đội
class InvitePlayerAPIView(APIView):
    def post(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
            player_id = request.data.get('player_id')
            player = Player.objects.get(id=player_id)

            invite = PlayerInvite.objects.create(
                team=team,
                player=player,
                expire_date=request.data.get('expire_date')
            )
            serializer = PlayerInviteSerializer(invite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

# Chấp nhận lời mời người chơi
class AcceptPlayerInviteAPIView(APIView):
    def post(self, request, invite_id):
        try:
            invite = PlayerInvite.objects.get(id=invite_id)
            player = invite.player
            team = invite.team
            player.team = team
            player.save()
            invite.delete()
            return Response({"detail": "Player invite accepted."}, status=status.HTTP_200_OK)
        except PlayerInvite.DoesNotExist:
            return Response({"detail": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)     

# Yêu cầu tham gia đội
class RequestJoinTeamAPIView(APIView):
    def post(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
            player_id = request.data.get('player_id')

            # Validate player existence
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                return Response({'error': 'Player not found'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a team request
            team_request = TeamRequest.objects.create(
                team=team,
                player=player,
                expire_date=request.data.get('expire_date'),
                message=request.data.get('message', ''),
                status='PENDING'
            )
            serializer = TeamRequestSerializer(team_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)


# Chấp nhận yêu cầu tham gia đội
class AcceptTeamRequestAPIView(APIView):
    def post(self, request, request_id):
        try:
            team_request = TeamRequest.objects.get(id=request_id)

            # Check the current status of the request
            if team_request.status != 'PENDING':
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

            # Accept the request
            player = team_request.player
            team = team_request.team
            player.team = team
            player.save()

            # Update the request status
            team_request.status = 'ACCEPTED'
            team_request.save()

            return Response({"detail": "Team request accepted."}, status=status.HTTP_200_OK)
        except TeamRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

# Tạo trận đấu mới
class CreateMatchAPIView(APIView):
    def post(self, request):
        match_data = request.data
        inviting_team = match_data['inviting_team']
        guest_team = match_data['guest_team']

        match = Match.objects.create(
            inviting_team=inviting_team,
            guest_team=guest_team,
            status='PENDING',
            created_at=match_data['created_at'],
            expires_at=match_data['expires_at']
        )
        serializer = MatchSerializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MatchScorePropositionAPIView(APIView):
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            my_team_id = request.data.get('my_team_id')
            my_score = request.data.get('my_score')
            opponent_score = request.data.get('opponent_score')

            my_team = match.inviting_team if my_team_id == match.inviting_team.id else match.guest_team
            match.update_proposition(my_team, my_score, opponent_score)
            return Response({"detail": "Score proposition updated successfully."}, status=status.HTTP_200_OK)
        except Match.DoesNotExist:
            return Response({"detail": "Match not found."}, status=status.HTTP_404_NOT_FOUND)