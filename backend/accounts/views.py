from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import UserProfiles, Friendships, StreakRescues, DEFAULT_AVATARS
from .serializers import ProfileSerializer, FriendRequestSerializer

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