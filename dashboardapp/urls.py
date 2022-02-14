from django.urls import path

from dashboardapp.views import DashboardCreateView, DashboardDetailView, AssetSummaryPieChartView

app_name = 'dashboardapp'

urlpatterns = [

    path('create/', DashboardCreateView.as_view(), name='create'),
    path('detail/<int:pk>', DashboardDetailView.as_view(), name='detail'),
    path('detail_asset_summary_pie_chart/', AssetSummaryPieChartView.as_view(), name='detail_asset_summary_pie_chart'),

]