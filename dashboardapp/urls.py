from django.urls import path

from dashboardapp.views import DashboardCreateView, DashboardDetailView, AssetSummaryPieChartView, AssetHistoryListView, \
    asset_history_excel_download, asset_history_excel_upload, AssetHistoryExcelUploadButton, AssetHistoryUpdateView, \
    AssetHistoryDeleteView, asset_history_delete_all, asset_history_capture

app_name = 'dashboardapp'

urlpatterns = [

    path('create/', DashboardCreateView.as_view(), name='create'),
    path('detail/<int:pk>', DashboardDetailView.as_view(), name='detail'),
    path('detail_asset_summary_pie_chart/', AssetSummaryPieChartView.as_view(), name='detail_asset_summary_pie_chart'),

    path('asset_history_list/', AssetHistoryListView.as_view(), name='asset_history_list'),
    path('asset_history_excel_download/', asset_history_excel_download, name='asset_history_excel_download'),
    path('asset_history_excel_upload/', asset_history_excel_upload, name='asset_history_excel_upload'),
    path('asset_history_excel_upload_button/', AssetHistoryExcelUploadButton.as_view(), name='asset_history_excel_upload_button'),
    path('asset_history_update/<int:pk>', AssetHistoryUpdateView.as_view(), name='asset_history_update'),
    path('asset_history_delete/<int:pk>', AssetHistoryDeleteView.as_view(), name='asset_history_delete'),
    path('asset_history_delete_all/', asset_history_delete_all, name='asset_history_delete_all'),
    path('asset_history_capture/', asset_history_capture, name='asset_history_capture'),

]