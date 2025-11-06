from django.urls import path
from .views import societies_collection, join_society, get_society

urlpatterns = [
    path('societies', societies_collection),
    path('societies/', societies_collection),
    path('societies/<str:id>', get_society),
    path('societies/<str:id>/join', join_society),
]
