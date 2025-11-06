from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    FriendViewSet,
    create_user,
    get_user_by_id,
    get_me,
    update_points,
    list_users,
    list_friends,
    list_friends_by_user,
    send_invite,
    accept_invite,
    create_challenge,
    sacrifice_points,
    auth_register,
    auth_login,
)

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

friend_view = FriendViewSet.as_view({
    'post': 'send_request',
    'post': 'accept_request',
    'get': 'list_requests',
    'post': 'rescue_streak',
})

urlpatterns = [
    path('api/auth/', include(router.urls)),
    # JWT Auth
    path('auth/register', auth_register, name='auth_register'),
    path('auth/login', auth_login, name='auth_login'),
    # Users API
    path('users', create_user, name='create_user'),  # POST create
    path('users/', list_users, name='list_users'),   # GET list
    path('users/mock', list_users, name='mock_users'),  # compatibility for frontend
    path('users/<str:id>/', get_user_by_id, name='get_user_by_id'),
    path('users/me/', get_me, name='get_me'),
    path('users/points/', update_points, name='update_points'),
    # Friends API (root paths to match frontend)
    path('friends', list_friends, name='list_friends'),
    path('friends/<str:userId>', list_friends_by_user, name='list_friends_by_user'),
    path('friends/invite', send_invite, name='send_invite'),
    path('friends/accept', accept_invite, name='accept_invite'),
    path('friends/challenge', create_challenge, name='create_challenge'),
    path('friends/sacrifice', sacrifice_points, name='sacrifice_points'),
]