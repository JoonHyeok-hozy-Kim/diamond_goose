from django.urls import path

from householdbookapp.views import LiquidityListView, HouseholdbookHomeView, LiquidityCreateView, LiquidityUpdateView, \
    LiquidityDeleteView, LiquidityPieChartView, DebtListView, DebtCreateView, DebtUpdateView, DebtDeleteView, \
    DebtPieChartView, HouseholdbookChartView, IncomeExpenseListView, IncomeExpenseCreateView, IncomeExpenseDeleteView, \
    IncomeExpenseUpdateView, IncomeExpenseTabularInsert, income_expense_delete_all, income_expense_excel_download, \
    IncomeExpenseExcelUploadButton, income_expense_excel_upload, IncomeExpenseGridChartView

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
    path('income_expense_tabular_insert/', IncomeExpenseTabularInsert.as_view(), name='income_expense_tabular_insert'),
    path('income_expense_update/<int:pk>', IncomeExpenseUpdateView.as_view(), name='income_expense_update'),
    path('income_expense_delete/<int:pk>', IncomeExpenseDeleteView.as_view(), name='income_expense_delete'),
    path('income_expense_delete_all/', income_expense_delete_all, name='income_expense_delete_all'),
    path('income_expense_excel_download/', income_expense_excel_download, name='income_expense_excel_download'),
    path('income_expense_excel_upload_button/', IncomeExpenseExcelUploadButton.as_view(), name='income_expense_excel_upload_button'),
    path('income_expense_excel_upload/', income_expense_excel_upload, name='income_expense_excel_upload'),
    path('income_expense_grid_chart/', IncomeExpenseGridChartView.as_view(), name='income_expense_grid_chart'),

]