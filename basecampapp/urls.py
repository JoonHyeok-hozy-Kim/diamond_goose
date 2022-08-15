from django.urls import path

from basecampapp.views import about_this_view

app_name = "basecampapp"

urlpatterns = [
    path('about_this/', about_this_view, name='about_this'),

]