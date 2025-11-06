from django.contrib import admin
from .models import AssetCards, EventCards, SpendingCards, SavingsCards


@admin.register(AssetCards)
class AssetCardsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "purchase_cost", "profit_per_return", "max_returns")
    search_fields = ("name",)


@admin.register(EventCards)
class EventCardsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "effect_points", "type", "rarity")
    search_fields = ("title",)


@admin.register(SpendingCards)
class SpendingCardsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "total_cost")
    search_fields = ("name",)


@admin.register(SavingsCards)
class SavingsCardsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "save_threshold")
    search_fields = ("name",)

# Register your models here.
