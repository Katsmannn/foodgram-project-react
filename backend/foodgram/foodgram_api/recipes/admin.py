from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    pass
