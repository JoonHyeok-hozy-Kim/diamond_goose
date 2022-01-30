from django.urls import path

from assetapp.views import AssetCreateView, AssetDetailView, AssetDeleteView, AssetTransactionCreateView, \
    AssetTransactionDeleteView, assettransaction_delete_all

app_name = 'assetapp'

urlpatterns = [

    path('asset_create/', AssetCreateView.as_view(), name='asset_create'),
    path('asset_detail/<int:pk>', AssetDetailView.as_view(), name='asset_detail'),
    path('asset_delete/<int:pk>', AssetDeleteView.as_view(), name='asset_delete'),

    path('assettransaction_create', AssetTransactionCreateView.as_view(), name='assettransaction_create'),
    path('assettransaction_delete/<int:pk>', AssetTransactionDeleteView.as_view(), name='assettransaction_delete'),
    path('assettransaction_delete_all/', assettransaction_delete_all, name='assettransaction_delete_all'),

    # path('assettransaction_export_csv_template/', Assettransaction_export_csv_template, name='assettransaction_export_csv_template'),
    # path('assettransaction_import_csv/', Assettransaction_import_csv, name='assettransaction_import_csv'),

]