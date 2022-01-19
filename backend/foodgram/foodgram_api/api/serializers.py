from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from .utils import add_ingredients_tags, get_user_and_recipe_from_serializer
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipesIngredient, Tag)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователей.
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    ERROR_ME_USERNAME = {
        'username': 'the username "me" is not allowed'}

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                self.ERROR_ME_USERNAME
            )
        return value

    class Meta:
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        ]
        model = User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей. Чтение.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        ]
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(
                author=obj, user=user
            ).exists()
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    """
    Подготовка ингредиентов для рецептов. Создание/изменение.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipesIngredient
        fields = [
            'id',
            'amount',
        ]


class RecipeIngredientsSerializerRead(serializers.ModelSerializer):
    """
    Подготовка ингредиентов для рецептов. Чтение.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredient
        fields = [
            'id',
            'name',
            'amount',
            'measurement_unit',
        ]


class RecipesSerializerRead(serializers.ModelSerializer):
    """
    Сериализатор для рецептов. Чтение.
    """
    author = UserSerializer(
        read_only=True
    )
    tags = TagsSerializer(
        many=True
    )
    ingredients = RecipeIngredientsSerializerRead(
        source='recipesingredient_set',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    text = serializers.CharField(
        source='description'
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'name',
            'text',
            'tags',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            1 if user.is_authenticated
            and Favorite.objects.filter(
                recipe=obj, user=user
            ).exists() else 0
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            1 if user.is_authenticated
            and Cart.objects.filter(
                recipe=obj,
                user=user
            ).exists() else 0
        )


class RecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов. Создание/изменение.
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True,
    )
    ingredients = RecipesIngredientsSerializer(
        many=True,
        required=True
    )
    text = serializers.CharField(
        source='description'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'text',
            'tags',
            'ingredients',
            'cooking_time',
            'image',
        ]
        read_only_fields = ('author', )

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=validated_data['author'],
            name=validated_data['name'],
            description=validated_data['description'],
            cooking_time=validated_data['cooking_time'],
            image=validated_data['image']
        )
        return add_ingredients_tags(
            recipe,
            validated_data,
            RecipesIngredient
        )[0]

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipesIngredient.objects.filter(recipe=instance.id).delete()
        instance, validated_data = add_ingredients_tags(
            instance,
            validated_data,
            RecipesIngredient
        )
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializerRead(
            instance, context=context
        ).data

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'must be positive'
            )
        return value

    def validate_ingredients(self, value):
        for ingredient in value:
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    'amount must be positive'
                )
        return value


class RecipesForSubscribeSerializer(serializers.ModelSerializer):
    """
    Подготовка рецептов для подписок пользователя.
    """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Просмотр подписок пользователя.
    """
    id = serializers.ReadOnlyField(source='author.id')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')

    class Meta:
        model = Subscription
        fields = [
            'id',
            'username',
            'first_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        read_only_fields = [
            'id',
            'username',
            'first_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_is_subscribed(self, obj):
        return 1

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        user = request.user
        limit = request.GET.get('recipes_limit')
        if limit is not None:
            queryset = Recipe.objects.filter(
                author__recipe_author__user=user
            )[:int(limit)]
        else:
            queryset = Recipe.objects.filter(
                author__recipe_author__user=user
            )
        return RecipesForSubscribeSerializer(queryset, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Подписки. Создание/удаление.
    """
    username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Subscription
        fields = ['username']
        read_only_fields = ['author', 'user']

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionsSerializer(
            instance, context=context
        ).data

    def validate(self, data):
        context = self.context
        author_id = int(context.get('view').kwargs['author_id'])
        user_id = context.get('request').user.id
        if author_id == user_id:
            raise serializers.ValidationError(
                detail='Subscribe to yourself not allowed'
            )
        if Subscription.objects.filter(
            author=author_id,
            user=user_id
        ).exists():
            raise serializers.ValidationError(
                detail='You have already subscribed to the author'
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    """
    Обработка корзины покупок пользователя.
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Cart
        fields = ['id', 'name', 'cooking_time']

    def validate(self, data):
        recipe_id, user_id = get_user_and_recipe_from_serializer(self)
        if Cart.objects.filter(recipe=recipe_id, user=user_id).exists():
            raise serializers.ValidationError(
                detail='The recipe is already in the cart'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Обработка списка избранных рецептов пользователя.
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'cooking_time']

    def validate(self, data):
        recipe_id, user_id = get_user_and_recipe_from_serializer(self)
        if Favorite.objects.filter(recipe=recipe_id, user=user_id).exists():
            raise serializers.ValidationError(
                detail='The recipe is already in the favorite list'
            )
        return data
