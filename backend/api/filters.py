import django_filters as filters

from recipes.models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецептов.
    """

    is_favorited = filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.CharFilter(
        method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart', )

    def filter_is_favorited(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по избранным.
        """

        user = self.request.user
        if value == 1 and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        elif value == 0:
            return queryset.exclude(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по наличию в списке покупок.
        """

        user = self.request.user
        if value == 1 and user.is_authenticated:
            return queryset.filter(in_shopping_carts__user=user)
        elif value == 0:
            return queryset.exclude(in_shopping_carts__user=user)
        return queryset

    def filter_tags(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по тегам.
        """

        tags = self.request.query_params.getlist('tags')
        if tags:
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset


class IngredientFilter(filters.FilterSet):
    """
    Фильтр для ингредиентов.
    """

    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = '__all__'
