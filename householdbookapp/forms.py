from django.forms import ModelForm

from householdbookapp.models import Liquidity, Debt


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