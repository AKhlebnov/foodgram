from rest_framework.pagination import PageNumberPagination


class PageNumberWithLimitPagination(PageNumberPagination):
    """
    Кастомная пагинация с номером страницы и лимитом
    на количество элементов на странице.
    """

    page_size_query_param = 'limit'
