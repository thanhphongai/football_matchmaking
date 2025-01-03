from django.urls import path
from .views import AcceptPlayerInviteAPIView, AcceptTeamRequestAPIView, CreateMatchAPIView, CreatePlayerAPIView, CreateTeamAPIView, InvitePlayerAPIView, MatchDetailAPIView, MatchScorePropositionAPIView, RequestJoinTeamAPIView, TeamChallengeAPIView, TeamDetailView, TeamListView

urlpatterns = [
    path('api/teams/<int:id>/', TeamDetailView.as_view(), name='team_detail'),
    path('api/teams/', TeamListView.as_view(), name='team_detail'),
    path('api/teams/<int:id>/challenge/', TeamChallengeAPIView.as_view(), name='team_challenge'),
    path('api/matches/<int:id>/', MatchDetailAPIView.as_view(), name='match_detail'),
    path('api/matches/<int:id>/score-proposition/', MatchScorePropositionAPIView.as_view(), name='match_score_proposition'),
    path('api/create_player/', CreatePlayerAPIView.as_view(), name='create_player'),
    path('api/create_team/', CreateTeamAPIView.as_view(), name='create_team'),
    path('api/teams/<int:team_id>/invite_player/', InvitePlayerAPIView.as_view(), name='team_invite_player'),
    path('api/teams/<int:team_id>/request_join/', RequestJoinTeamAPIView.as_view(), name='team_request_join'),
    path('api/player_invitations/<int:invite_id>/accept/', AcceptPlayerInviteAPIView.as_view(), name='accept_player_invite'),
    path('api/team_requests/<int:request_id>/accept/', AcceptTeamRequestAPIView.as_view(), name='accept_team_request'),
    path('api/matches/create/', CreateMatchAPIView.as_view(), name='create_match'),
]
