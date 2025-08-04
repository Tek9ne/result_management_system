from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from results.models import Profile

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role='student')  # Create with default role
    # Only save if profile exists and needs update, avoiding issues with missing fields
    if hasattr(instance, 'profile'):
        instance.profile.save()