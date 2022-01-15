from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _

from users.models import User


class Tags(models.Model):

    name = models.CharField(
        max_length=256,
        verbose_name='tag'
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='slug'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredients(models.Model):

    name = models.CharField(
        max_length=50
    )
    measurement_unit = models.CharField(
        max_length=50
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipes(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author'
    )
    name = models.CharField(
        max_length=150,
    )
    image = models.ImageField(
        upload_to='recipes/',
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(
        to=Ingredients,
        through='RecipesIngredients'
    )
    tags = models.ManyToManyField(
        Tags
    )
    cooking_time = models.PositiveIntegerField(
    )
    pub_time = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ['-pub_time']

    def __str__(self):
        return self.name


class RecipesIngredients(models.Model):

    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()


class Cart(models.Model):

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='cart_recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_user')


class Favorite(models.Model):

    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='favorite_recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_user')
