from django.db import models

from users.models import User


class Tag(models.Model):

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
        verbose_name = 'Тэги'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name='name',
        max_length=150
    )
    measurement_unit = models.CharField(
        verbose_name='measurement_unit',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author'
    )
    name = models.CharField(
        max_length=150,
        verbose_name='name'
    )
    image = models.ImageField(
        verbose_name='image',
        upload_to='recipes/',
    )
    description = models.TextField(
        verbose_name='description'
    )
    ingredients = models.ManyToManyField(
        verbose_name='recipe_ingredient',
        to=Ingredient,
        through='RecipesIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='recipe_tag',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='cooking_time'
    )
    pub_time = models.DateTimeField(
        verbose_name='pub_date',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_time']

    def __str__(self):
        return self.name


class RecipesIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='ingredient'
    )
    amount = models.PositiveIntegerField(
        verbose_name='amount'
    )

    class Meta:
        verbose_name = 'Состав'
        verbose_name_plural = 'Состав'
        models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredient_in_recipe'
        )


class Cart(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user',
        verbose_name='user'
    )

    class Meta:
        verbose_name = 'Покупки'
        verbose_name_plural = 'Покупки'
        models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_sopping_cart'
        )


class Favorite(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='user'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorited'
        )
