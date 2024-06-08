from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """
    Встроенное представление для ингредиентов рецепта в админ-панели.
    """

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления рецептами.
    """

    list_display = (
        'name', 'author', 'cooking_time', 'get_favorites_count', 'created_at'
    )
    search_fields = ('name', 'author__username')
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags', )
    list_filter = ('tags',)

    def get_favorites_count(self, obj):
        """
        Метод получения количества добавлений рецепта в избранное.
        """
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'Рецепт в избранном, кол-во'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления ингредиентами.
    """

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления тегами.
    """

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
