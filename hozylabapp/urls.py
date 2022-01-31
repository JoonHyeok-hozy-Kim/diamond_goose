from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from hozylabapp.views import lab_home_view, TempTransactionListView, upload_excel_daeshin, upload_excel_hankook, \
    upload_excel_shinhan, upload_mass_transaction

app_name = "hozylabapp"

urlpatterns = [

    path('lab_home/', lab_home_view, name='lab_home'),
    path('temptransaction_list/', TempTransactionListView.as_view(), name='temptransaction_list'),

    path('upload_mass_transaction/', upload_mass_transaction, name='upload_mass_transaction'),
    path('upload_excel_daeshin/', upload_excel_daeshin, name='upload_excel_daeshin'),
    path('upload_excel_hankook/', upload_excel_hankook, name='upload_excel_hankook'),
    path('upload_excel_shinhan/', upload_excel_shinhan, name='upload_excel_shinhan'),


    # path('upload_excel_shinhan_foreignstock/', upload_excel_shinhan_foreignstock, name='upload_excel_shinhan_foreignstock'),

    # path('temptransaction_detail/', TempTransactionDetailView.as_view(), name='temptransaction_detail'),

]