from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserCreateSerializer

from drf_extra_fields.fields import Base64ImageField
from users.models import User, Subscriptions
from recipes.models import (
    Tags,
    Ingredients,
    Recipes,
    RecipesIngredients,
    Cart,
    Favorite
)


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
            and Subscriptions.objects.filter(
                author=obj, user=user
            ).exists()
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    """
    Подготовка ингредиентов для рецептов. Создание/изменение.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = RecipesIngredients
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
        model = RecipesIngredients
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
        source='recipesingredients_set',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    text = serializers.CharField(
        source='description'
    )

    class Meta:
        model = Recipes
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
        queryset=Tags.objects.all(),
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
        model = Recipes
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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = ingredient['id']
            current_ingredient_amount = ingredient['amount']
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=current_ingredient_amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get(
            'name', instance.name
        )
        instance.description = validated_data.get(
            'text', instance.description
        )
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get(
            'image', instance.image
        )
        instance.save()
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.all().delete
            instance.tags.set(tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            RecipesIngredients.objects.filter(recipe=instance.id).delete()
            for ingredient in ingredients:
                current_ingredient = ingredient['id']
                current_ingredient_amount = ingredient['amount']
                RecipesIngredients.objects.create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=current_ingredient_amount
                )
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
        model = Recipes
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
        model = Subscriptions
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
        return Recipes.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        user = request.user
        limit = request.GET.get('recipes_limit')
        if limit is not None:
            queryset = Recipes.objects.filter(
                author__recipe_author__user=user
            )[:int(limit)]
        else:
            queryset = Recipes.objects.filter(
                author__recipe_author__user=user
            )
        return RecipesForSubscribeSerializer(queryset, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Подписки. Создание/удаление.
    """
    username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Subscriptions
        fields = ['username']
        read_only_fields = ['author', 'user']

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionsSerializer(
            instance, context=context
        ).data


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
