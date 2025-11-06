# accounts/serializers.py
from rest_framework import serializers
from .models import Users, UserProfiles, Friendships, StreakRescues

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    societies = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    
    class Meta:
        model = UserProfiles
        fields = ['pesa_points', 'profession', 'societies', 'streak_days', 'avatar_url', 'total_dreams_unlocked', 'user']

class FriendRequestSerializer(serializers.ModelSerializer):
    friend = UserSerializer()
    class Meta:
        model = Friendships
        fields = ['id', 'friend', 'status', 'requested_at']