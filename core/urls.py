from django.urls import path

from . import product_views

app_name = "products"

urlpatterns = [
    path("", product_views.ProductListView.as_view(), name="product_list"),
    path("new/", product_views.ProductCreateView.as_view(), name="product_create"),
    path(
        "<int:pk>/edit/",
        product_views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "<int:pk>/delete/",
        product_views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
]
