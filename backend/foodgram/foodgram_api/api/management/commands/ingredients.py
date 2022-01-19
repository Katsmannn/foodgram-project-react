import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Внесение ингредиентов из файла foodgram/data/ingredients.json
    в базу данных.
    """
    help = 'Ingredients'

    def handle(self, *args, **options):
        file = open('../data/ingredients.json')
        data = json.load(file)
        for elem in data:
            Ingredient.objects.create(
                name=elem['name'],
                measurement_unit=elem[
                    'measurement_unit'
                ]
            )
        file.close()

