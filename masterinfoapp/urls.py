from django.urls import path

from masterinfoapp.views import AssetMasterCreateView, AssetMasterListView, AssetMasterDetailView, \
    AssetMasterUpdateView, AssetMasterDeleteView, CurrencyMasterCreateView, CurrencyMasterListView, \
    CurrencyMasterUpdateView, PensionMasterCreateView, PensionMasterListView, PensionMasterUpdateView

app_name = 'masterinfoapp'

urlpatterns = [

    path('assetmaster_create/', AssetMasterCreateView.as_view(), name='assetmaster_create'),
    path('assetmaster_list/', AssetMasterListView.as_view(), name='assetmaster_list'),
    path('assetmaster_detail/<int:pk>', AssetMasterDetailView.as_view(), name='assetmaster_detail'),
    path('assetmaster_update/<int:pk>', AssetMasterUpdateView.as_view(), name='assetmaster_update'),
    path('assetmaster_delete/<int:pk>', AssetMasterDeleteView.as_view(), name='assetmaster_delete'),

    path('currencymaster_create/', CurrencyMasterCreateView.as_view(), name='currencymaster_create'),
    path('currencymaster_list/', CurrencyMasterListView.as_view(), name='currencymaster_list'),
    path('currencymaster_update/<int:pk>', CurrencyMasterUpdateView.as_view(), name='currencymaster_update'),

    path('pensionmaster_create/', PensionMasterCreateView.as_view(), name='pensionmaster_create'),
    path('pensionmaster_list/', PensionMasterListView.as_view(), name='pensionmaster_list'),
    path('pensionmaster_update/<int:pk>', PensionMasterUpdateView.as_view(), name='pensionmaster_update'),

]