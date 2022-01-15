from django.core.management.base import BaseCommand
import json
from recipes.models import Tags


class Command(BaseCommand):
    """
    Внесение ингредиентов из файла foodgram/data/tags.json
    в базу данных.
    """
    help = 'Tags'

    def handle(self, *args, **options):
        file = open('../data/tags.json')
        data = json.load(file)
        for elem in data:
            Tags.objects.create(
                name=elem['name'].encode('cp1251').decode(),
                color=elem['color'],
                slug=elem['slug'],
            )
        file.close()
