from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Page-number pagination shared by every API list endpoint.

    Clients may override the page size up to ``max_page_size`` using the
    ``page_size`` query parameter.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
