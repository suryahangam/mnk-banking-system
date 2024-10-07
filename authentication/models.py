import pyotp
from django.db import models
from django.contrib.auth.models import (AbstractUser,
                                        AbstractBaseUser)
from django.db import models

from authentication.custom_manager import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    mobile_number = models.CharField(max_length=15, blank=True,
                                     null=True, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    two_factor_enabled = models.BooleanField(default=True)
    otp_secret = models.CharField(max_length=255,
                                  default=pyotp.random_base32)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """
        Override the save method to assign the admin 
        role to the first created user.
        """
        if not CustomUser.objects.exists():
            self.is_admin = True
        super().save(*args, **kwargs)
