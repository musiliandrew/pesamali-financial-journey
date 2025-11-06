from django.contrib import admin
from .models import ShopItems, ShopPurchases

@admin.register(ShopItems)
class ShopItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_points", "rarity")
    search_fields = ("name",)

@admin.register(ShopPurchases)
class ShopPurchasesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item", "price_points", "purchased_at")
    search_fields = ("user__username", "item__name")
