import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


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
            Tag.objects.create(
                name=elem['name'],
                color=elem['color'],
                slug=elem['slug'],
            )
        file.close()

