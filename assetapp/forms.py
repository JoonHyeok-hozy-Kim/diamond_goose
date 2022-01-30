from django.forms import ModelForm
from django.forms import widgets

from assetapp.models import Asset, AssetTransaction


class AssetCreationForm(ModelForm):
    class Meta:
        model = Asset
        fields = []


class AssetTransactionCreationForm(ModelForm):

    def __init__(self, *args, **kwargs):
       super(AssetTransactionCreationForm, self).__init__(*args, **kwargs)
       # self.fields['quantity'].widget.attrs['readonly'] = True

    class Meta:
        model = AssetTransaction
        fields = [
            'transaction_type',
            'quantity',
            'price',
            'dividend_amount',
            'split_ratio_one_to_N',
            'transaction_date',
            'transaction_fee',
            'transaction_tax',
            'note',
        ]

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }

