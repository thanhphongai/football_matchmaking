from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    mail = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return self.name + ' ' + self.surname


class Team(models.Model):
    name = models.CharField(max_length=120)
    is_public = models.BooleanField(default=True)
    score = models.IntegerField(default=0)

    @property
    def matches(self):
        return Match.objects.filter(inviting_team=self) | Match.objects.filter(guest_team=self)

    @property
    def played_matches(self):
        return self.matches.exclude(inviting_score__isnull=True).exclude(guest_score__isnull=True)

    @property
    def planned_matches(self):
        return self.matches.filter(inviting_score__isnull=True).filter(guest_score__isnull=True)

    def update_score(self):
        self.score = self.inviting_matches.aggregate(sum=Coalesce(Sum('inviting_score'), 0))['sum'] + \
                     self.guest_matches.aggregate(sum=Coalesce(Sum('guest_score'), 0))['sum']
        self.save()

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="players")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="players")

    def __str__(self):
        return f"{self.user.name} in {self.team.name if self.team else 'No Team'}"


class ScoreProposition(models.Model):
    inviting_score = models.IntegerField(null=True, blank=True)
    guest_score = models.IntegerField(null=True, blank=True)

    suggesting_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Match(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateField(default=timezone.now)
    expires_at = models.DateField(null=True, blank=True)
    suggested_at = models.DateField(null=True, blank=True)
    inviting_score = models.IntegerField(null=True, blank=True)
    guest_score = models.IntegerField(null=True, blank=True)

    inviting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='inviting_matches', null=True, blank=True)
    guest_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='guest_matches', null=True, blank=True)

    host_proposition = models.OneToOneField(ScoreProposition, null=True, blank=True, on_delete=models.SET_NULL, related_name='match_h')
    guest_proposition = models.OneToOneField(ScoreProposition, null=True, blank=True, on_delete=models.SET_NULL, related_name='match_g')

    def other_team(self, my_team):
        return self.guest_team if my_team == self.inviting_team else self.inviting_team

    def my_score_proposition(self, my_team):
        return self.host_proposition if my_team == self.inviting_team else self.guest_proposition

    def opponent_score_proposition(self, my_team):
        return self.guest_proposition if my_team == self.inviting_team else self.host_proposition

    def update_proposition(self, team, my_score, opponent_score):
        if team == self.inviting_team:
            if self.host_proposition:
                self.host_proposition.inviting_score = my_score
                self.host_proposition.guest_score = opponent_score
                self.host_proposition.save()
            else:
                self.host_proposition = ScoreProposition(inviting_score=my_score, guest_score=opponent_score, suggesting_team=team)
                self.host_proposition.save()
        elif team == self.guest_team:
            if self.guest_proposition:
                self.guest_proposition.inviting_score = opponent_score
                self.guest_proposition.guest_score = my_score
                self.guest_proposition.save()
            else:
                self.guest_proposition = ScoreProposition(inviting_score=opponent_score, guest_score=my_score, suggesting_team=team)
                self.guest_proposition.save()

        if self.guest_proposition and self.host_proposition:
            if (self.guest_proposition.guest_score == self.host_proposition.guest_score and
                    self.guest_proposition.inviting_score == self.host_proposition.inviting_score):
                self.inviting_score = self.host_proposition.inviting_score
                self.guest_score = self.guest_proposition.guest_score

        self.save()
        self.inviting_team.update_score()
        self.guest_team.update_score()

        return True

    def __str__(self):
        return f"{self.inviting_team.name} vs. {self.guest_team.name}"


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="events")
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=100)  # e.g., "Goal", "Penalty"
    description = models.TextField(blank=True, null=True)


class PlayerInvite(models.Model):
    expire_date = models.DateField(null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class TeamRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]

    expire_date = models.DateField(null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    message = models.TextField(null=True, blank=True)  # Optional message from the player




