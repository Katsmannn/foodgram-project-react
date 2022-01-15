from django.contrib.auth.models import AbstractUser
from django.db import models
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

    class Meta:
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Subscriptions(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
