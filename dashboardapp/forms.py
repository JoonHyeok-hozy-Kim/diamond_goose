from django.forms import ModelForm, widgets

from dashboardapp.models import Dashboard, AssetHistory


class DashboardCreationForm(ModelForm):
    class Meta:
        model = Dashboard
        fields = [
            'main_currency',
            'initial_date',
        ]

        widgets = {
            'initial_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }


class AssetHistoryCreationForm(ModelForm):
    class Meta:
        model = AssetHistory
        fields = [
            'capture_date',
            'total_asset_amount',
            'total_liquidity_amount',
            'total_investment_amount',
            'total_debt_amount',
            'net_capital_amount',
        ]

        widgets = {
            'capture_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }


class AssetHistoryCaptureForm(ModelForm):
    class Meta:
        model = AssetHistory
        fields = []

# capture_date
# total_asset_amount
# total_liquidity_amount
# total_investment_amount
# total_debt_amount
# net_capital_amount