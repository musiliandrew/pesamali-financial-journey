from django.db import models
from django.utils import timezone
import uuid

# Predefined Professions
PROFESSIONS = [
    ('teacher', 'Teacher'),
    ('farmer', 'Farmer'),
    ('engineer', 'Engineer'),
    ('doctor', 'Doctor'),
    ('artist', 'Artist'),
    ('entrepreneur', 'Entrepreneur'),
    ('writer', 'Writer'),
    ('athlete', 'Athlete'),
]

# Default Avatars (free)
DEFAULT_AVATARS = [
    "avatars/teacher_1.png",
    "avatars/farmer_1.png",
    "avatars/engineer_1.png",
    # ... add 10+
]

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class UserProfiles(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    pesa_points = models.BigIntegerField(default=0)
    profession = models.CharField(max_length=20, choices=PROFESSIONS, default='teacher')
    societies = models.ManyToManyField('societies.Societies', related_name='members', blank=True)
    streak_days = models.IntegerField(default=0)
    streak_saved_at = models.DateField(null=True, blank=True)
    avatar_url = models.CharField(max_length=255, default=DEFAULT_AVATARS[0])
    total_dreams_unlocked = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_profiles'

    def save(self, *args, **kwargs):
        if not self.streak_saved_at:
            self.streak_saved_at = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class StreakRescues(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    savior = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='rescues_given')
    saved = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='rescues_received')
    points_sacrificed = models.IntegerField(default=50)
    rescued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'streak_rescues'
        unique_together = ('savior', 'saved', 'rescued_at')


class Friendships(models.Model):
    STATUSES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests_sent')
    friend = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=10, choices=STATUSES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'friendships'
        unique_together = ('user', 'friend')