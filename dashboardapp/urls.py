from django.urls import path

from dashboardapp.views import DashboardCreateView, DashboardDetailView, AssetSummaryPieChartView, AssetHistoryListView, \
    asset_history_excel_download, asset_history_excel_upload, AssetHistoryExcelUploadButton

app_name = 'dashboardapp'

urlpatterns = [

    path('create/', DashboardCreateView.as_view(), name='create'),
    path('detail/<int:pk>', DashboardDetailView.as_view(), name='detail'),
    path('detail_asset_summary_pie_chart/', AssetSummaryPieChartView.as_view(), name='detail_asset_summary_pie_chart'),

    path('asset_history_list/', AssetHistoryListView.as_view(), name='asset_history_list'),
    path('asset_history_excel_download/', asset_history_excel_download, name='asset_history_excel_download'),
    path('asset_history_excel_upload/', asset_history_excel_upload, name='asset_history_excel_upload'),
    path('asset_history_excel_upload_button/', AssetHistoryExcelUploadButton.as_view(), name='asset_history_excel_upload_button'),


]