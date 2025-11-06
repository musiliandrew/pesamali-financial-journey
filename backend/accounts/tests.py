from django.test import TestCase
from accounts.models import Users, UserProfiles

class StreakTest(TestCase):
    def test_streak_buy(self):
        user = Users.objects.create(username='test')
        profile = user.userprofiles
        profile.pesa_points = 200
        profile.save()
        # Simulate buy
        profile.buy_streak()
        self.assertEqual(profile.streak_days, 1)