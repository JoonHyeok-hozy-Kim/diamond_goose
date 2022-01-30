from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accountapp.views import temp_welcome_view, AccountCreateView, AccountUpdateView, AccountDeleteView, \
    AccountDetailView, ProfileCreateView, ProfileUpdateView

app_name = "accountapp"

urlpatterns = [
    path('temp_welcome/', temp_welcome_view, name='temp_welcome'),

    path('account_create/',AccountCreateView.as_view(),name='account_create'),
    path('account_update/<int:pk>',AccountUpdateView.as_view(),name='account_update'),
    path('account_delete/<int:pk>',AccountDeleteView.as_view(),name='account_delete'),
    path('account_detail/<int:pk>',AccountDetailView.as_view(),name='account_detail'),

    path('login/', LoginView.as_view(template_name='accountapp/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile_create/', ProfileCreateView.as_view(), name='profile_create'),
    path('profile_update/<int:pk>', ProfileUpdateView.as_view(), name='profile_update'),

]