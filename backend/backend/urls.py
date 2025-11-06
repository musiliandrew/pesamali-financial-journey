from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('', include('game.urls')),
    path('', include('accounts.urls')),
    path('', include('cards.urls')),
    path('', include('dreams.urls')),
    path('', include('societies.urls')),
    path('', include('leaderboard.urls')),
    path('', include('qa.urls')),
    path('', include('shop.urls')),
]
