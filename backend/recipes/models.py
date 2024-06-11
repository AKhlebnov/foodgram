from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError

from foodgram.constants import (
    MAX_INGREDIENT_M_U, MAX_INGREDIENT_NAME,
    MAX_RECIPE_NAME, MAX_TAG_FIELD, MIN_VALIDATOR_VALUE)

from .validators import validate_custom_string

User = get_user_model()


class Tag(models.Model):
    """
    Модель для тегов.
    """

    name = models.CharField('Название', max_length=MAX_TAG_FIELD)
    slug = models.SlugField(
        'Слаг', max_length=MAX_TAG_FIELD,
        unique=True,
        db_index=True,
        validators=[validate_custom_string]
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель для ингредиентов.
    """

    name = models.CharField(
        'Название', max_length=MAX_INGREDIENT_NAME, db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_INGREDIENT_M_U
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель для рецептов.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        'Название', max_length=MAX_RECIPE_NAME, db_index=True
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        validators=[MinValueValidator(MIN_VALIDATOR_VALUE)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для ингредиентов/рецептов.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(MIN_VALIDATOR_VALUE)]
    )

    class Meta:
        unique_together = ['recipe', 'ingredient']
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class Favorite(models.Model):
    """
    Модель для избранных рецептов.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"


class ShoppingCart(models.Model):
    """
    Модель для корзины покупок.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='in_shopping_carts'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"


class Subscription(models.Model):
    """
    Модель для подписок.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user__exact=models.F('author')),
                name='prevent_subscription',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"Подписка: {self.user.username} на {self.author.username}"

    def clean(self):
        super().clean()
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')
