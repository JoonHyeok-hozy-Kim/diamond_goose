from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from accountapp.decorators import account_ownership_required, profile_ownership_required
from accountapp.forms import AccountUpdateForm, ProfileCreationForm
from accountapp.models import Profile

has_account_ownership = [login_required, account_ownership_required]
has_profile_ownership = [login_required, profile_ownership_required]


def temp_welcome_view(request):
    return render(request, 'accountapp/temp_welcome.html')

class AccountCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    success_url = reverse_lazy('accountapp:login')
    template_name = 'accountapp/account_create.html'


@method_decorator(has_account_ownership,'get')
@method_decorator(has_account_ownership,'post')
class AccountUpdateView(UpdateView):
    model = User
    form_class = AccountUpdateForm
    context_object_name = 'target_user'
    template_name = 'accountapp/account_update.html'

    def get_success_url(self):
        return reverse('accountapp:account_detail', kwargs={'pk': self.object.user.pk})


@method_decorator(has_account_ownership,'get')
@method_decorator(has_account_ownership,'post')
class AccountDeleteView(DeleteView):
    model = User
    context_object_name = 'target_user'
    success_url = reverse_lazy('accountapp:account_create')
    template_name = 'accountapp/account_delete.html'


class AccountDetailView(DetailView):
    model = User
    context_object_name = 'target_user'
    template_name = 'accountapp/account_detail.html'


class ProfileCreateView(CreateView):
    model = Profile
    form_class = ProfileCreationForm
    context_object_name = 'target_profile'
    template_name = 'accountapp/profile_create.html'

    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accountapp:account_detail', kwargs={'pk': self.object.user.pk})


@method_decorator(has_profile_ownership, 'get')
@method_decorator(has_profile_ownership, 'post')
class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileCreationForm
    context_object_name = 'target_profile'
    template_name = 'accountapp/profile_update.html'

    def get_success_url(self):
        return reverse('accountapp:account_detail', kwargs={'pk': self.object.user.pk})
