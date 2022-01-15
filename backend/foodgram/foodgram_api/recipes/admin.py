from django.contrib import admin

from .models import Recipes, Favorite, Tags, Ingredients


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    pass


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass
