from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, UserProfiles

@receiver(post_save, sender=Users)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfiles.objects.create(user=instance)