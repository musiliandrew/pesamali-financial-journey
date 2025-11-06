from django.db import models

class GameLogs(models.Model):
    id = models.UUIDField(primary_key=True)
    room = models.ForeignKey('GameRooms', models.DO_NOTHING, blank=True, null=True)
    turn = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_logs'


class GamePlayers(models.Model):
    id = models.UUIDField(primary_key=True)
    room = models.ForeignKey('GameRooms', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    seat = models.IntegerField(blank=True, null=True, default=0)
    starting_points = models.BigIntegerField(blank=True, null=True)
    current_points = models.BigIntegerField(blank=True, null=True)
    savings = models.BigIntegerField(blank=True, null=True)
    liabilities = models.BigIntegerField(blank=True, null=True)
    assets = models.JSONField(blank=True, null=True)
    spending_cards = models.JSONField(blank=True, null=True)
    savings_cards = models.JSONField(blank=True, null=True)
    tokens = models.JSONField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)
    is_cpu = models.BooleanField(blank=True, null=True)
    ready = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_players'


class GameRooms(models.Model):
    id = models.UUIDField(primary_key=True)
    dream = models.ForeignKey('dreams.Dreams', models.DO_NOTHING, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    winner = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    player_count = models.IntegerField(blank=True, null=True)
    current_turn = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        managed = True
        db_table = 'game_rooms'

