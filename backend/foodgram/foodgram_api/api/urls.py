from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, FavoriteViewSet, FoodgramUserViewSet,
                    IngredientsViewSet, RecipesViewSet, SubscribeViewSet,
                    SubscriptionsListViewSet, TagsViewSet,
                    download_shopping_cart)


api_router = DefaultRouter()

api_router.register(r'users/(?P<author_id>\d+)/subscribe',
                    SubscribeViewSet, basename='download')
api_router.register('users', FoodgramUserViewSet, basename='users')
api_router.register('tags', TagsViewSet, basename='tags')
api_router.register('ingredients', IngredientsViewSet, basename='ingredients')
api_router.register('recipes', RecipesViewSet, basename='recipes')
api_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                    FavoriteViewSet, basename='favorite')
api_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                    CartViewSet, basename='cart')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download'
    ),
    path('users/subscriptions/', SubscriptionsListViewSet.as_view()),
    path('', include(api_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
