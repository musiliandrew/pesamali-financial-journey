from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, FriendViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

friend_view = FriendViewSet.as_view({
    'post': 'send_request',
    'post': 'accept_request',
    'get': 'list_requests',
    'post': 'rescue_streak',
})

urlpatterns = [
    path('', include(router.urls)),
    path('friends/', friend_view, name='friends'),
]