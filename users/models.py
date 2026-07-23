from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    custom user model
    empty for now but allows us to add or customize the fields
    without replacing Django's authentication system.
    """

    email = models.EmailField(unique=True)

    pass
