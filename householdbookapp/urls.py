from django.urls import path

from householdbookapp.views import LiquidityListView, HouseholdbookHomeView, LiquidityCreateView, LiquidityUpdateView, \
    LiquidityDeleteView, LiquidityPieChartView

app_name = "householdbookapp"

urlpatterns = [

    path('householdbook_home/', HouseholdbookHomeView.as_view(), name='householdbook_home'),

    path('liquidity_list/', LiquidityListView.as_view(), name='liquidity_list'),
    path('liquidity_create/', LiquidityCreateView.as_view(), name='liquidity_create'),
    path('liquidity_update/<int:pk>', LiquidityUpdateView.as_view(), name='liquidity_update'),
    path('liquidity_delete/<int:pk>', LiquidityDeleteView.as_view(), name='liquidity_delete'),
    path('liquidity_pie_chart/', LiquidityPieChartView.as_view(), name='liquidity_pie_chart'),

]