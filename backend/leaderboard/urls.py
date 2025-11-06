from django.urls import path
from .views import leaderboard_global, leaderboard_by_profession

urlpatterns = [
    path('leaderboard/global', leaderboard_global),
    path('leaderboard/profession/<str:profession>', leaderboard_by_profession),
]
