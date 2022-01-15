from django.core.management.base import BaseCommand
import json
from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Ingredients'

    def handle(self, *args, **options):
        file = open('../data/ingredients.json')
        data = json.load(file)
        for elem in data:
            Ingredients.objects.create(
                name=elem['name'].encode('cp1251').decode(),
                measurement_unit=elem[
                    'measurement_unit'
                ].encode('cp1251').decode()
            )
        file.close()
