from django.urls import path

from dashboardapp.views import DashboardCreateView, DashboardDetailView

app_name = 'dashboardapp'

urlpatterns = [

    path('create/', DashboardCreateView.as_view(), name='create'),
    path('detail/<int:pk>', DashboardDetailView.as_view(), name='detail'),

]