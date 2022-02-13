from django.urls import path

from householdbookapp.views import LiquidityListView, HouseholdbookHomeView, LiquidityCreateView, LiquidityUpdateView, \
    LiquidityDeleteView, LiquidityPieChartView, DebtListView, DebtCreateView, DebtUpdateView, DebtDeleteView, \
    DebtPieChartView, HouseholdbookChartView, IncomeExpenseListView, IncomeExpenseCreateView, IncomeExpenseDeleteView, \
    IncomeExpenseUpdateView

app_name = "householdbookapp"

urlpatterns = [

    path('householdbook_home/', HouseholdbookHomeView.as_view(), name='householdbook_home'),
    path('householdbook_chart/', HouseholdbookChartView.as_view(), name='householdbook_chart'),

    path('liquidity_list/', LiquidityListView.as_view(), name='liquidity_list'),
    path('liquidity_create/', LiquidityCreateView.as_view(), name='liquidity_create'),
    path('liquidity_update/<int:pk>', LiquidityUpdateView.as_view(), name='liquidity_update'),
    path('liquidity_delete/<int:pk>', LiquidityDeleteView.as_view(), name='liquidity_delete'),
    path('liquidity_pie_chart/', LiquidityPieChartView.as_view(), name='liquidity_pie_chart'),

    path('debt_list/', DebtListView.as_view(), name='debt_list'),
    path('debt_create/', DebtCreateView.as_view(), name='debt_create'),
    path('debt_update/<int:pk>', DebtUpdateView.as_view(), name='debt_update'),
    path('debt_delete/<int:pk>', DebtDeleteView.as_view(), name='debt_delete'),
    path('debt_pie_chart/', DebtPieChartView.as_view(), name='debt_pie_chart'),

    path('income_expense_list/', IncomeExpenseListView.as_view(), name='income_expense_list'),
    path('income_expense_create/', IncomeExpenseCreateView.as_view(), name='income_expense_create'),
    path('income_expense_update/<int:pk>', IncomeExpenseUpdateView.as_view(), name='income_expense_update'),
    path('income_expense_delete/<int:pk>', IncomeExpenseDeleteView.as_view(), name='income_expense_delete'),
    # path('income_expense_pie_chart/', IncomeExpensePieChartView.as_view(), name='income_expense_pie_chart'),

]