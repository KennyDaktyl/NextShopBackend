from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from web.models.accounts import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print('create_user')
    if created:
        print('create_profile')
        Profile.objects.get_or_create(user=instance)
