from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    first_name = models.CharField(
        verbose_name='first_name',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='last_name',
        max_length=150
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True
    )

    REQUIRED_FIELDS = ['last_name', 'first_name', 'email']

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Subscriptions(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='author'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(
            fields=['author', 'user'],
            name='unique_subscription'
        )
