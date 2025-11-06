from django.contrib import admin
from .models import Dreams, UserDreams


@admin.register(Dreams)
class DreamsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "cost", "order_index", "prerequisite_dream")
    search_fields = ("name", "slug")


@admin.register(UserDreams)
class UserDreamsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dream", "unlocked_at")
    search_fields = ("user__username", "dream__name")

# Register your models here.
