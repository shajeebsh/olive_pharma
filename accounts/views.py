from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from django.urls import reverse_lazy

from .forms import ProfileForm
from .models import UserProfile


class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
