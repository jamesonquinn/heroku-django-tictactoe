from django.db import models

from scenario import SCENARIOS

VERSION = 1

class Election(models.Model):
    scenario_name = models.CharField(max_len=20)
    system_name = models.CharField(max_len=20)
    
    patient = models.BooleanField()
    
    started = models.DateTimeField(auto_now_add=True)
    voters_registered = models.DateTimeField(null=True)
    
class Round(models.Model):
    election = models.ForeignKey(Election)
    round_num = models.IntegerField()
    
    started = models.DateTimeField(auto_now_add=True)
    votes_complete = models.DateTimeField(null=True)
    
    winner = models.IntegerField(null=True)
    
    code_version = models.IntegerField(default=VERSION)
    
    class meta:
        unique_together = (election, round_num)
    
class Voter(models.Model):
    election = models.ForeignKey(Election)
    session_key = models.CharField(max_len=40, unique=True)
    has_connected = models.BooleanField(default=False)
    has_broken = models.BooleanField(default=False)

class Vote(models.Model):
    round = models.ForeignKey(Round)
    voter = models.ForeignKey(Voter)
    
    broken = models.BooleanField(default=False)
    
    vote = JsonField()
    
    class meta:
        unique_together = (round, voter)