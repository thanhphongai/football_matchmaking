from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import PlayerInvite, Team, Match, Player, TeamRequest, User

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Team, Player, Match, PlayerInvite, TeamRequest, User


class TeamDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.team = Team.objects.create(name="Test Team", is_public=True)

    def test_get_team_detail_success(self):
        response = self.client.get(f'/api/teams/{self.team.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Team")

    def test_get_team_detail_not_found(self):
        response = self.client.get('/api/teams/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TeamChallengeAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.inviting_team = Team.objects.create(name="Inviting Team", is_public=True)
        self.guest_team = Team.objects.create(name="Guest Team", is_public=True)

    def test_post_team_challenge_success(self):
        response = self.client.post(f'/api/teams/{self.inviting_team.id}/challenge/', {
            'guest_team_id': self.guest_team.id,
            'created_at': '2024-12-22',
            'expires_at': '2024-12-23'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_post_team_challenge_invalid_team(self):
        response = self.client.post('/api/teams/999/challenge/', {
            'guest_team_id': self.guest_team.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MatchDetailAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.inviting_team = Team.objects.create(name="Inviting Team", is_public=True)
        self.guest_team = Team.objects.create(name="Guest Team", is_public=True)
        self.match = Match.objects.create(
            inviting_team=self.inviting_team,
            guest_team=self.guest_team,
            status='PENDING'
        )

    def test_get_match_detail_success(self):
        response = self.client.get(f'/api/matches/{self.match.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_get_match_detail_not_found(self):
        response = self.client.get('/api/matches/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreatePlayerAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_player_success(self):
        response = self.client.post('/api/create_player/', {
            'name': 'John',
            'surname': 'Doe',
            'mail': 'john.doe@example.com'
        }, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class InvitePlayerAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.team = Team.objects.create(name="Test Team", is_public=True)
        user = User.objects.create(name='Jane', surname='Doe', mail='jane.doe@example.com')
        self.player = Player.objects.create(user=user)

    def test_invite_player_success(self):
        response = self.client.post(f'/api/teams/{self.team.id}/invite_player/', {
            'player_id': self.player.id,
            'expire_date': '2024-12-30'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invite_player_team_not_found(self):
        response = self.client.post('/api/teams/999/invite_player/', {
            'player_id': self.player.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AcceptPlayerInviteAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create(name='Jane', surname='Doe', mail='jane.doe@example.com')
        self.player = Player.objects.create(user=user)
        self.team = Team.objects.create(name="Test Team", is_public=True)
        self.invite = PlayerInvite.objects.create(player=self.player, team=self.team, expire_date='2024-12-30')

    def test_accept_player_invite_success(self):
        response = self.client.post(f'/api/player_invitations/{self.invite.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team, self.team)


    def test_accept_player_invite_not_found(self):
        response = self.client.post('/api/player_invitations/999/accept/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RequestJoinTeamAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create(name='Mark', surname='Smith', mail='mark.smith@example.com')
        self.player = Player.objects.create(user=user)
        self.team = Team.objects.create(name="Joinable Team", is_public=True)

    def test_request_join_team_success(self):
        response = self.client.post(f'/api/teams/{self.team.id}/request_join/', {
            'player_id': self.player.id,
            'message': 'I would like to join your team.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_request_join_team_not_found(self):
        response = self.client.post('/api/teams/999/request_join/', {
            'player_id': self.player.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_request_join_team_invalid_player(self):
        response = self.client.post(f'/api/teams/{self.team.id}/request_join/', {
            'player_id': 999
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AcceptTeamRequestAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create(name='Emma', surname='Brown', mail='emma.brown@example.com')
        self.player = Player.objects.create(user=user)
        self.team = Team.objects.create(name="Test Team", is_public=True)
        self.request = TeamRequest.objects.create(player=self.player, team=self.team, status='PENDING')

    def test_accept_team_request_success(self):
        response = self.client.post(f'/api/team_requests/{self.request.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team, self.team)

    def test_accept_team_request_invalid_status(self):
        self.request.status = 'ACCEPTED'
        self.request.save()

        response = self.client.post(f'/api/team_requests/{self.request.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid status', response.data.get('error', ''))

    def test_accept_team_request_request_not_found(self):
        response = self.client.post('/api/team_requests/999/accept/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Request not found', response.data.get('error', ''))
