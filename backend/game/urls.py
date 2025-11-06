from django.urls import path
from . import views

urlpatterns = [
    path("matches", views.create_match),
    path("matches/<str:match_id>/join", views.join_match),
    path("matches/<str:match_id>/start", views.start_match),
    path("matches/<str:match_id>/state", views.get_state),
    path("matches/<str:match_id>/roll", views.roll_dice),
    path("matches/<str:match_id>/move", views.move_token),
    path("matches/<str:match_id>/select-asset", views.select_asset),
]
