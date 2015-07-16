from django.db.models.signals import post_save
from django.dispatch import receiver
from www.models import Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)