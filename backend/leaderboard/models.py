from django.db import models

class LeaderboardGlobal(models.Model):
    user = models.OneToOneField('accounts.Users', models.DO_NOTHING, primary_key=True)
    pesa_points = models.BigIntegerField(blank=True, null=True)
    dreams_unlocked = models.IntegerField(blank=True, null=True)
    games_won = models.IntegerField(blank=True, null=True)
    week_start = models.DateField()

    class Meta:
        managed = True
        db_table = 'leaderboard_global'


class LeaderboardSociety(models.Model):
    id = models.BigAutoField(primary_key=True)
    society = models.ForeignKey('societies.Societies', models.DO_NOTHING)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING)
    pesa_points = models.BigIntegerField(blank=True, null=True)
    week_start = models.DateField()

    class Meta:
        managed = True
        db_table = 'leaderboard_society'
        unique_together = (('society', 'user', 'week_start'),)
