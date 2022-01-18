def add_ingredients_tags(obj, data, model):
    """
    Добавление ингедиентов и тэгов к рецепту.

    obj - объект рецепта, в который необходимо добавить нгредиент/тэг,
    data - словарь, содежащий ключи 'ingredients' и 'tags',
    model - модель, связывающая рецепт и ингредиенты (RecipesIngredients)
    """
    ingredients = data.pop('ingredients')
    tags = data.pop('tags')
    obj.tags.set(tags)
    for ingredient in ingredients:
        current_ingredient = ingredient['id']
        current_ingredient_amount = ingredient['amount']
        model.objects.create(
            recipe=obj,
            ingredient=current_ingredient,
            amount=current_ingredient_amount
        )
    return [obj, data]


def get_user_and_recipe_from_serializer(serializer):
    """
    Получение id рецепта и id пользователя из сериализатора.
    """
    context = serializer.context
    recipe_id = int(context.get('view').kwargs['recipe_id'])
    user_id = context.get('request').user.id
    return [recipe_id, user_id]
