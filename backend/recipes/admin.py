from django.contrib import admin
from .models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    Subscription,
    RecipeIngredient
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1  # Количество дополнительных пустых форм для добавления


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)  # Для удобного выбора тегов


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
