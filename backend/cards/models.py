from django.db import models

class AssetCards(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    purchase_cost = models.BigIntegerField()
    profit_per_return = models.BigIntegerField()
    max_returns = models.IntegerField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'asset_cards'
        

class EventCards(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.TextField()
    effect_points = models.BigIntegerField()
    message = models.TextField()
    type = models.TextField(blank=True, null=True)
    rarity = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'event_cards'
        
class SpendingCards(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    total_cost = models.BigIntegerField()
    breakdown = models.JSONField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'spending_cards'
        
class SavingsCards(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    save_threshold = models.BigIntegerField()
    bonus_condition = models.JSONField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'savings_cards'
