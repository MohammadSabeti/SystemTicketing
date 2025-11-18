import os

from django.contrib.auth.models import AbstractUser
from django.db import models

def user_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'profile_{instance.username}.{ext}'
    return os.path.join('profile_pics', filename)

class RoleChoices(models.TextChoices):
    USER = 'user', 'User'
    SUPPORT = 'support', 'Support'
    ADMIN = 'admin', 'Admin'

class UserProfile(AbstractUser):
    role = models.CharField(max_length=20,
                            choices=RoleChoices.choices,
                            default=RoleChoices.USER)
    profile_image = models.ImageField(upload_to=user_profile_image_path,
                                      blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
