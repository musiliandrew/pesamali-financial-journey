from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Users, UserProfiles, Friendships, StreakRescues, DEFAULT_AVATARS, PROFESSIONS
from rest_framework.decorators import api_view
from django.db import transaction

from .serializers import ProfileSerializer, FriendRequestSerializer
from .auth import generate_jwt
from django.contrib.auth.hashers import make_password, check_password

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfiles.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = UserProfiles.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_avatar(self, request):
        profile = request.user.userprofiles
        avatar = request.data.get('avatar_url')
        if avatar in DEFAULT_AVATARS:
            profile.avatar_url = avatar
            profile.save()
            return Response({'status': 'avatar updated'})
        return Response({'error': 'Invalid avatar'}, status=400)

    @action(detail=False, methods=['post'])
    def buy_streak(self, request):
        profile = request.user.userprofiles
        cost = 100
        if profile.pesa_points >= cost:
            profile.pesa_points -= cost
            profile.streak_saved_at = timezone.now().date()
            profile.streak_days += 1
            profile.save()
            return Response({'status': 'streak bought'})
        return Response({'error': 'not enough points'}, status=400)


# --- Friends API matching frontend paths ---

@api_view(["GET"])  # GET /friends
def list_friends(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    friends = Friendships.objects.filter(user=request.user, status='ACCEPTED').select_related('friend')
    return Response({
        "friends": [{
            "id": str(f.friend.id),
            "username": f.friend.username,
        } for f in friends]
    })


# --- Auth (JWT) ---

@api_view(["POST"])  # POST /auth/register
def auth_register(request):
    data = request.data or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    profession = data.get("profession")
    if not username or not password:
        return Response({"detail": "username and password required"}, status=400)
    if Users.objects.filter(username=username).exists():
        return Response({"detail": "username taken"}, status=400)
    try:
        with transaction.atomic():
            user = Users.objects.create(username=username, email=email, password_hash=make_password(password))
            # Use provided profession value as-is to satisfy existing DB CHECK constraints.
            # Fallback to a conservative value likely present in legacy constraints.
            p_val = str(profession) if profession else 'teacher_highschool'
            profile = UserProfiles.objects.create(user=user, profession=p_val)
    except Exception as e:
        return Response({"detail": f"registration_failed: {str(e)}"}, status=400)
    token = generate_jwt(user)
    return Response({"token": token, "user": {"id": str(user.id), "username": user.username}})


@api_view(["POST"])  # POST /auth/login
def auth_login(request):
    data = request.data or {}
    username = data.get("username")
    password = data.get("password")
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return Response({"detail": "invalid credentials"}, status=401)
    if not check_password(password or "", user.password_hash):
        return Response({"detail": "invalid credentials"}, status=401)
    token = generate_jwt(user)
    return Response({"token": token, "user": {"id": str(user.id), "username": user.username}})


@api_view(["GET"])  # GET /friends/<userId>
def list_friends_by_user(request, userId: str):
    try:
        user = Users.objects.get(id=userId)
    except Users.DoesNotExist:
        return Response({"detail": "user not found"}, status=404)
    friends = Friendships.objects.filter(user=user, status='ACCEPTED').select_related('friend')
    return Response({
        "friends": [{
            "id": str(f.friend.id),
            "username": f.friend.username,
        } for f in friends]
    })


@api_view(["POST"])  # POST /friends/invite
def send_invite(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    friend_id = request.data.get('friend_id')
    try:
        friend = Users.objects.get(id=friend_id)
    except Users.DoesNotExist:
        return Response({"detail": "friend not found"}, status=404)
    fr, created = Friendships.objects.get_or_create(user=request.user, friend=friend, defaults={'status': 'PENDING'})
    if not created:
        return Response({"detail": "already requested"}, status=400)
    return Response({"ok": True})


@api_view(["POST"])  # POST /friends/accept
def accept_invite(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    request_id = request.data.get('request_id')
    try:
        fr = Friendships.objects.get(id=request_id, friend=request.user, status='PENDING')
    except Friendships.DoesNotExist:
        return Response({"detail": "request not found"}, status=404)
    fr.status = 'ACCEPTED'
    fr.accepted_at = timezone.now()
    fr.save(update_fields=['status', 'accepted_at'])
    return Response({"ok": True})


@api_view(["POST"])  # POST /friends/challenge
def create_challenge(request):
    # Placeholder: persist a challenge entity if/when model exists
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    # Accept and validate payload (toUserId, questionId, etc.)
    return Response({"ok": True})


@api_view(["POST"])  # POST /friends/sacrifice
def sacrifice_points(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    to_user_id = request.data.get('to_user_id')
    amount = int(request.data.get('amount', 50))
    try:
        to_user = Users.objects.get(id=to_user_id)
        to_profile = UserProfiles.objects.get(user=to_user)
        from_profile = UserProfiles.objects.get(user=request.user)
    except (Users.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "user not found"}, status=404)
    if (from_profile.pesa_points or 0) < amount:
        return Response({"detail": "not enough points"}, status=400)
    with transaction.atomic():
        from_profile.pesa_points -= amount
        to_profile.streak_saved_at = timezone.now().date()
        to_profile.streak_days = (to_profile.streak_days or 0) + 1
        from_profile.save(update_fields=["pesa_points"])
        to_profile.save(update_fields=["streak_saved_at", "streak_days"])
        StreakRescues.objects.create(savior=request.user, saved=to_user, points_sacrificed=amount)
    return Response({"ok": True})


# --- User API (non-mock) ---

@api_view(["POST"])  # POST /users
def create_user(request):
    data = request.data or {}
    username = data.get("username")
    email = data.get("email")
    raw_password = data.get("password", "")
    if not username:
        return Response({"detail": "username required"}, status=400)
    with transaction.atomic():
        user = Users.objects.create(username=username, email=email, password_hash=make_password(raw_password) if raw_password else "")
        profile = UserProfiles.objects.create(user=user)
    return Response({
        "id": str(user.id),
        "username": user.username,
        "profession": profile.profession,
        "pesamaliPoints": profile.pesa_points,
        "avatar": profile.avatar_url,
    }, status=201)


@api_view(["GET"])  # GET /users/<id>
def get_user_by_id(request, id: str):
    try:
        user = Users.objects.get(id=id)
        profile = UserProfiles.objects.get(user=user)
    except (Users.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "not found"}, status=404)
    return Response({
        "id": str(user.id),
        "username": user.username,
        "profession": profile.profession,
        "pesamaliPoints": profile.pesa_points,
        "avatar": profile.avatar_url,
    })


@api_view(["GET"])  # GET /users/me (requires auth)
def get_me(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    try:
        profile = UserProfiles.objects.get(user=request.user)
    except UserProfiles.DoesNotExist:
        return Response({"detail": "profile not found"}, status=404)
    return Response({
        "id": str(request.user.id),
        "username": request.user.username,
        "profession": profile.profession,
        "pesamaliPoints": profile.pesa_points,
        "avatar": profile.avatar_url,
    })


@api_view(["POST"])  # POST /users/points
def update_points(request):
    data = request.data or {}
    user_id = data.get("userId")
    delta = int(data.get("delta", 0))
    if not user_id:
        return Response({"detail": "userId required"}, status=400)
    try:
        user = Users.objects.get(id=user_id)
        profile = UserProfiles.objects.get(user=user)
    except (Users.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "not found"}, status=404)
    profile.pesa_points = (profile.pesa_points or 0) + delta
    profile.save(update_fields=["pesa_points"])
    return Response({"ok": True, "pesamaliPoints": profile.pesa_points})


@api_view(["GET"])  # GET /users (compat for listing instead of mock)
def list_users(request):
    profiles = UserProfiles.objects.select_related("user").all()[:50]
    return Response({
        "users": [{
            "id": str(p.user.id),
            "username": p.user.username,
            "profession": p.profession,
            "pesamaliPoints": p.pesa_points,
            "avatar": p.avatar_url,
            "online": True,
        } for p in profiles]
    })


class FriendViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def send_request(self, request):
        friend_id = request.data['friend_id']
        friendship, created = Friendships.objects.get_or_create(
            user=request.user, friend_id=friend_id, defaults={'status': 'PENDING'}
        )
        if created:
            return Response({'status': 'request sent'})
        return Response({'error': 'already sent'}, status=400)

    @action(detail=False, methods=['post'])
    def accept_request(self, request):
        req_id = request.data['request_id']
        friendship = Friendships.objects.get(id=req_id, friend=request.user, status='PENDING')
        friendship.status = 'ACCEPTED'
        friendship.accepted_at = timezone.now()
        friendship.save()
        return Response({'status': 'friend added'})

    @action(detail=False, methods=['get'])
    def list_requests(self, request):
        requests = Friendships.objects.filter(friend=request.user, status='PENDING')
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def rescue_streak(self, request):
        friend_id = request.data['friend_id']
        friend_profile = UserProfiles.objects.get(user_id=friend_id)
        if request.user.userprofiles.pesa_points >= 50:
            request.user.userprofiles.pesa_points -= 50
            friend_profile.streak_saved_at = timezone.now().date()
            friend_profile.streak_days += 1
            friend_profile.save()
            StreakRescues.objects.create(savior=request.user, saved_id=friend_id)
            return Response({'status': 'streak saved'})
        return Response({'error': 'not enough points'}, status=400)