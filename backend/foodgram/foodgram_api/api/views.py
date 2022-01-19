from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet

from .filters import IngredientsFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipesSerializer,
                          RecipesSerializerRead, SubscribeSerializer,
                          SubscriptionsSerializer, TagsSerializer)
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipesIngredient, Tag)
from users.models import Subscription, User


class CartFavoriteBaseViewSet(viewsets.ModelViewSet):
    """
    Базовый вьюсет для корзины покупок и для избранного.
    """
    queryset = None
    serializer_class = None

    def perform_create(self, serializer):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(recipe=recipe, user=user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        recipe_id = self.kwargs.get('recipe_id')
        object = get_object_or_404(
            queryset,
            recipe=recipe_id,
            user=self.request.user
        )
        self.perform_destroy(object)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodgramUserViewSet(UserViewSet):
    """
    Обработка пользователей.
    """

    @action(["get", "delete"], detail=False,
            permission_classes=[CurrentUserOrAdmin], name='me')
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Обработка тэгов.
    """
    serializer_class = TagsSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadOnly]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Обработка ингредиентов.
    """
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Обработка рецептов.
    """
    serializer_class = RecipesSerializerRead
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = PageLimitPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipesSerializerRead
        return RecipesSerializer

    def update(self, *args, **kwargs):
        raise MethodNotAllowed('PUT', detail='PUT method not allowed')

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)


class SubscriptionsListViewSet(generics.ListAPIView):
    """
    Посмотр подписок пользователя.
    """
    serializer_class = SubscriptionsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Обработка подписок пользователя (создание/удаление).
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
        serializer.save(author=author, user=user)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs.get('author_id')
        subscribe_object = get_object_or_404(
            Subscription,
            author=author_id,
            user=self.request.user
        )
        self.perform_destroy(subscribe_object)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(CartFavoriteBaseViewSet):
    """
    Обработка корзины покупок.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


class FavoriteViewSet(CartFavoriteBaseViewSet):
    """
    Обработка списка избанных рецептов.
    """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    """
    Получение перечня ингредиентов для рецептов в корзине
    и отпавка в виде текстового файла.
    """
    user = request.user
    ingredients = RecipesIngredient.objects.filter(
        recipe__cart_recipe__user=user.id
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(Sum('amount'))
    if not ingredients.exists():
        return Response('Shopping cart is empty')
    text = 'Для приготовления выбранных рецептов Вам понадобится:\n\n'
    for ingredient in ingredients:
        text += (
            ingredient['ingredient__name'] + ' - '
            + str(ingredient['amount__sum']) + ' '
            + ingredient['ingredient__measurement_unit'] + '.\n'
        )
    return HttpResponse(text, content_type='text/plain')
