from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

