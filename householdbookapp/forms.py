from django.forms import ModelForm

from householdbookapp.models import Liquidity


class LiquidityCreationForm(ModelForm):
    class Meta:
        model = Liquidity
        fields = [
            'liquidity_type',
            'liquidity_name',
            'currency',
            'amount',
        ]