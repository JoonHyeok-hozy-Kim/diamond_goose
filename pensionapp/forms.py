from django.forms import widgets, ModelForm, ModelChoiceField, RadioSelect
from pensionapp.models import Pension, PensionTransaction, PENSION_TRANSACTION_TYPES


class PensionCreationForm(ModelForm):
    class Meta:
        model = Pension
        fields = ['pension_master']


class PensionTransactionCreationForm(ModelForm):
    class Meta:
        model = PensionTransaction
        fields = ['transaction_type', 'amount', 'transaction_date']
        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }


# class PensionAssetCreationForm(ModelForm):
#     class Meta:
#         model = PensionAsset
#         fields = []
#
#
# class PensionAssetTransactionCreationForm(ModelForm):
#     class Meta:
#         model = PensionAssetTransaction
#         fields = ['transaction_type', 'quantity', 'price', 'transaction_fee', 'transaction_tax', 'transaction_date', 'note']
#
#         widgets = {
#             'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
#         }