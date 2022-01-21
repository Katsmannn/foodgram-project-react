from rest_framework.serializers import ImageField


class ImageFieldForRecipeRead(ImageField):

    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, 'use_url', True)
        if use_url:
            try:
                url = value.url
            except AttributeError:
                return None
            return url

        return value.name
