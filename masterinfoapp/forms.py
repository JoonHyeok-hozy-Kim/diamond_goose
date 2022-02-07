from django.forms import ModelForm

from masterinfoapp.models import AssetMaster, CurrencyMaster, PensionMaster


class AssetMasterCreationForm(ModelForm):
    class Meta:
        model = AssetMaster
        fields = [
            'asset_type',
            'etf_flag',
            'market',
            'ticker',
            'name',
            'currency',
            'image',
            'pension_asset_flag',
            'pension_risk_asset_flag',
        ]


class CurrencyMasterCreationForm(ModelForm):
    class Meta:
        model = CurrencyMaster
        fields = [
            'currency_code',
            'currency_name',
            'currency_sign',
            'currency_national_flag',
            'country',
        ]


class PensionMasterCreationForm(ModelForm):
    class Meta:
        model = PensionMaster
        fields = [
            'pension_type',
            'pension_name',
            'risk_ratio_force_flag',
            'risk_ratio',
            'color_hex',
        ]
