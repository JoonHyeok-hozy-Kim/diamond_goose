from django.urls import path

from exchangeapp.views import MyExchangeDetailView, ForeignCurrencyCreateView, MyExchangeCurrencyMasterListView, \
    MyExchangeCurrencyMasterDetailView, ForeignCurrencyDeleteView, ForeignCurrencyDetailView, \
    ForeignCurrencyTransactionCreateView, ForeignCurrencyTransactionDeleteView, foreign_currency_transaction_delete_all

app_name = 'exchangeapp'

urlpatterns = [

    path('myexchange_detail/<int:pk>', MyExchangeDetailView.as_view(), name='myexchange_detail'),
    path('myexchange_currencymaster_list/', MyExchangeCurrencyMasterListView.as_view(), name='myexchange_currencymaster_list'),
    path('myexchange_currencymaster_detail/<int:pk>', MyExchangeCurrencyMasterDetailView.as_view(), name='myexchange_currencymaster_detail'),

    path('foreigncurrency_create/', ForeignCurrencyCreateView.as_view(), name='foreigncurrency_create'),
    path('foreigncurrency_delete/<int:pk>', ForeignCurrencyDeleteView.as_view(), name='foreigncurrency_delete'),
    path('foreigncurrency_detail/<int:pk>', ForeignCurrencyDetailView.as_view(), name='foreigncurrency_detail'),
    # path('foreigncurrency_refresh/', foreign_currency_refresh, name='foreigncurrency_refresh'),
    # path('portfolio_refresh/<int:portfolio_pk>', portfolio_refresh, name='portfolio_refresh'),

    path('foreigncurrencytransaction_create/', ForeignCurrencyTransactionCreateView.as_view(), name='foreigncurrencytransaction_create'),
    path('foreigncurrencytransaction_delete/<int:pk>', ForeignCurrencyTransactionDeleteView.as_view(), name='foreigncurrencytransaction_delete'),
    path('foreigncurrencytransaction_delete_all/', foreign_currency_transaction_delete_all, name='foreigncurrencytransaction_delete_all'),

]