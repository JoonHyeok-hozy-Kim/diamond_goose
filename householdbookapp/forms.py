from django import forms
from django.forms import ModelForm
from django.forms import widgets

from householdbookapp.models import Liquidity, Debt, IncomeExpense


class LiquidityCreationForm(ModelForm):
    class Meta:
        model = Liquidity
        fields = [
            'liquidity_type',
            'liquidity_name',
            'currency',
            'amount',
        ]


class DebtCreationForm(ModelForm):
    class Meta:
        model = Debt
        fields = [
            'debt_name',
            'long_term_debt_flag',
            'currency',
            'amount',
        ]


class IncomeExpenseCreationForm(ModelForm):
    class Meta:
        model = IncomeExpense
        fields = [
            'period_name',
            'income_labor',
            'income_capital',
            'income_etc',
            'expense_housing_communication',
            'expense_living',
            'expense_grocery',
            'expense_shopping',
            'expense_leisure',
            'expense_health',
            'expense_largess',
            'expense_transportation',
            'expense_alcohol',
            'expense_education',
            'expense_car',
            'expense_financial',
            'expense_love_affair',
            'expense_etc',
        ]

        widgets = {
            'period_name': widgets.DateTimeInput(attrs={'type': 'month'}),
        }


class IncomeExpenseTabularInsertForm(forms.Form):
    period_name = forms.CharField(widget=forms.DateTimeInput(attrs={'type': 'month'}))

    total_income_amount = forms.FloatField()
    income_labor = forms.FloatField()
    income_capital = forms.FloatField()
    income_etc = forms.FloatField()

    total_expense_amount = forms.FloatField()
    expense_housing_communication = forms.FloatField()
    expense_living = forms.FloatField()
    expense_grocery = forms.FloatField()
    expense_shopping = forms.FloatField()
    expense_leisure = forms.FloatField()
    expense_health = forms.FloatField()
    expense_largess = forms.FloatField()
    expense_transportation = forms.FloatField()
    expense_alcohol = forms.FloatField()
    expense_education = forms.FloatField()
    expense_car = forms.FloatField()
    expense_financial = forms.FloatField()
    expense_love_affair = forms.FloatField()
    expense_etc = forms.FloatField()