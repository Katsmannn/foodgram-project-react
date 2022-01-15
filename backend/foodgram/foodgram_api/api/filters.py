from django_filters import rest_framework as filt

from recipes.models import Ingredients, Recipes


class RecipeFilter(filt.FilterSet):
    """
    Фильтр для рецептов.
    """
    author = filt.NumberFilter(
        field_name='author',
    )
    tags = filt.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='istartswith',
    )
    is_in_shopping_cart = filt.NumberFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )
    is_favorited = filt.NumberFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(cart_recipe__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(favorite_recipe__user=user)
        return queryset


class IngredientsFilter(filt.FilterSet):
    """
    Фильтр для ингредиентов.
    """
    name = filt.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredients
        fields = ('name',)
