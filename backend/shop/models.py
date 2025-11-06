from django.db import models

class ShopItems(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    price_points = models.IntegerField(default=0)
    image_url = models.TextField(blank=True, null=True)
    rarity = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shop_items'

class ShopPurchases(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING)
    item = models.ForeignKey(ShopItems, models.DO_NOTHING)
    price_points = models.IntegerField(default=0)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'shop_purchases'
