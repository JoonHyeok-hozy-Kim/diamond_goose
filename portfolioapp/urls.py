from django.urls import path

from portfolioapp.views import PortfolioCreateView, PortfolioDetailView, PortfolioAssetMasterListView, \
    PortfolioAssetMasterDetailView

app_name = 'portfolioapp'

urlpatterns = [

    path('portfolio_create/',PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio_detail/<int:pk>', PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolio_assetmaster_list/', PortfolioAssetMasterListView.as_view(), name='portfolio_assetmaster_list'),
    path('portfolio_assetmaster_detail/<int:pk>', PortfolioAssetMasterDetailView.as_view(), name='portfolio_assetmaster_detail'),

    # path('portfolio_refresh/', portfolio_refresh, name='portfolio_refresh'),

]