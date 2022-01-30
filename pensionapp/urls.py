from django.urls import path

from pensionapp.views import PensionCreateView, PensionListView, PensionDetailView, PensionTransactionCreateView, \
    PensionTransactionDeleteView

app_name = 'pensionapp'

urlpatterns = [

    # Pension Model Related Urls
    path('pension_create/', PensionCreateView.as_view(), name='pension_create'),
    path('pension_list/', PensionListView.as_view(), name='pension_list'),
    path('pension_detail/<int:pk>', PensionDetailView.as_view(), name='pension_detail'),
    # path('delete/<int:pk>',EquityTransactionDeleteView.as_view(),name='delete'),

    # PensionTransaction Model Related Urls
    path('pensiontransaction_create/', PensionTransactionCreateView.as_view(), name='pensiontransaction_create'),
    path('pensiontransaction_delete/<int:pk>', PensionTransactionDeleteView.as_view(),name='pensiontransaction_delete'),

    # PensionAsset Model Related Urls
    # path('pensionasset_list/<int:pension_pk>', PensionAssetListView.as_view(), name='pensionasset_list'),
    # path('pensionasset_create/<int:pension_pk>/<int:asset_pk>', PensionAssetCreateView.as_view(), name='pensionasset_create'),
    # path('pensionasset_delete/<int:pk>', PensionAssetDeleteView.as_view(), name='pensionasset_delete'),
    # path('pensionasset_detail/<int:pk>', PensionAssetDetailView.as_view(), name='pensionasset_detail'),

    # path('pensionassettransaction_create', PensionAssetTransactionCreateView.as_view(), name='pensionassettransaction_create'),
    # path('pensionassettransaction_delete/<int:pk>', PensionAssetTransactionDeleteView.as_view(), name='pensionassettransaction_delete'),

    # path('import_csv/', import_csv, name='import_csv'),
    # path('export_csv_template/', export_csv_template, name='export_csv_template'),
]