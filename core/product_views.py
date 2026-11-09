from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ProductForm
from .models import Product
from .permissions import RoleRequiredMixin


class ProductListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin",)
    model = Product
    template_name = "core/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(form__icontains=query)
                | Q(strength__icontains=query)
            )
        active = self.request.GET.get("active")
        if active in ("1", "0"):
            queryset = queryset.filter(active=active == "1")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["active_filter"] = self.request.GET.get("active", "")
        return context


class ProductCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ("admin",)
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Product created.")
        return super().form_valid(form)


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ("admin",)
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Product updated.")
        return super().form_valid(form)


class ProductDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ("admin",)
    model = Product
    template_name = "core/product_confirm_delete.html"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                self.request,
                "This product is used by sales records and cannot be deleted. "
                "Mark it inactive instead.",
            )
        else:
            messages.success(self.request, "Product deleted.")
        return redirect(self.get_success_url())
