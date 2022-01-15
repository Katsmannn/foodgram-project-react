from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    first_name = models.CharField(
        _('first name'),
        max_length=150
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )

    REQUIRED_FIELDS = ['last_name', 'first_name', 'email']


class Subscriptions(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_author')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')
