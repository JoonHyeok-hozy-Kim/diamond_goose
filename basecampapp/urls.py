from django.urls import path

from basecampapp.views import about_this_view, diamond_goose_home_view, SimulationAssetSummaryPieChartView, contact_view

app_name = "basecampapp"

urlpatterns = [
    path('about_this/', about_this_view, name='about_this'),

    path('diamond_goose_home/', diamond_goose_home_view, name='diamond_goose_home'),
    path('pie_chart_clone/', SimulationAssetSummaryPieChartView.as_view(), name='pie_chart_clone'),

    # path('contact/', contact_view, name='contact')

]