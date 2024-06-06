from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import Base64ImageField, UserSerializer

User = get_user_model


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для игредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для промежуточной модели рецепты/ингредиенты.
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи рецептов.
    """

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        """
        Метод для получения информации о том,
        добавлен ли рецепт в избранное пользователем.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Метод для получения информации о том,
        добавлен ли рецепт в список покупок пользователем.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCreateUpdateIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления ингредиентов рецепта.
    """

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeCreateUpdateIngredientSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'author',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        """
        Валидация входных данных сериализатора.
        """

        if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            ingredients = data.get('ingredients', [])
            tags = data.get('tags', [])

            for ingredient_data in ingredients:
                if ingredient_data['amount'] < 1:
                    raise serializers.ValidationError(
                        "Количество ингредиента не может быть меньше 1."
                    )

            ingredient_ids = [ingredient['id'] for ingredient in ingredients]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    "В списке ингредиентов есть повторяющиеся ингредиенты."
                )

            tag_ids = [tag.id for tag in tags]
            if len(tag_ids) != len(set(tag_ids)):
                raise serializers.ValidationError(
                    "В списке тегов есть повторяющиеся теги."
                )

            if not ingredients:
                raise serializers.ValidationError(
                    "Список ингредиентов не может быть пустым."
                )

            if not tags:
                raise serializers.ValidationError(
                    "Список тегов не может быть пустым."
                )

            cooking_time = data.get('cooking_time', 0)
            if cooking_time < 1:
                raise serializers.ValidationError(
                    "Время приготовления не может быть меньше 1 минуты."
                )

        ingredients = data.get('ingredients', [])

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    {
                        'ingredients':
                        f'Ингридиент с id {ingredient_id} не найден.'
                    }
                )

        return data

    def create(self, validated_data):
        """
        Метод для создания рецепта.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['id']
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        """
        Метод для изменения рецепта.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            RecipeIngredient.objects.filter(recipe=instance).delete()
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingredient_data['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Метод для выдачи сериализованных данных в нужном формате.
        """

        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор работы с избранным.
    """

    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """
        Валидация входных данных сериализатора.
        """

        user = self.context['request'].user
        recipe = self.context['recipe']

        if 'DELETE' in self.context['request'].method:
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Этот рецепт не был добавлен в избранное, '
                    'его нельзя удалить.'
                )

        if 'POST' in self.context['request'].method:
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Этот рецепт уже добавлен в избранное.'
                )

        return data

    def create(self, validated_data):
        """
        Метод для добавления в избранное.
        """

        user = self.context['request'].user
        recipe = self.context['recipe']
        favorite = Favorite.objects.create(user=user, recipe=recipe)
        return favorite

    def delete(self):
        """
        Метод для удаления из избранного.
        """

        user = self.context['request'].user
        recipe = self.context['recipe']
        Favorite.objects.filter(user=user, recipe=recipe).delete()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с корзиной.
    """

    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """
        Валидация входных данных сериализатора.
        """

        user = self.context['request'].user
        recipe = self.context['recipe']

        if 'DELETE' in self.context['request'].method:
            if not ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    'Этот рецепт не был добавлен в список покупок, '
                    'его нельзя удалить.'
                )

        if 'POST' in self.context['request'].method:
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Этот рецепт уже добавлен в список покупок.'
                )

        return data

    def create(self, validated_data):
        """
        Метод для добавления рецепта в корзину.
        """
        user = self.context['request'].user
        recipe = self.context['recipe']
        favorite = ShoppingCart.objects.create(user=user, recipe=recipe)
        return favorite

    def delete(self):
        """
        Метод для удаления рецепта из корзины.
        """
        user = self.context['request'].user
        recipe = self.context['recipe']
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
