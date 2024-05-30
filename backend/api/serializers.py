from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
from users.serializers import UserSerializer, Base64ImageField

User = get_user_model


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCreateUpdateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
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
        if self.context['request'].method in ['POST', 'PUT']:
            ingredients = data.get('ingredients', [])
            tags = data.get('tags', [])

            if not ingredients:
                raise serializers.ValidationError(
                    "Список ингредиентов не может быть пустым."
                )

            if not tags:
                raise serializers.ValidationError(
                    "Список тегов не может быть пустым."
                )

            # Проверка на наличие изображения
            if not data.get('image'):
                field_name = 'image'
                raise serializers.ValidationError(
                    {field_name: ["Обязательное поле."]}
                )

        ingredients = data.get('ingredients', [])

        # Проверка на существование ингредиентов
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
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        # Создаем рецепт
        recipe = Recipe.objects.create(**validated_data)

        # Создаем связанные ингредиенты
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['id']
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        # Создаем связанные теги
        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

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
        return RecipeSerializer(instance, context=self.context).data
