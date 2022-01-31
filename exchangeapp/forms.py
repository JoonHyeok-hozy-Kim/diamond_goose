from django.forms import widgets, ModelForm

from exchangeapp.models import ForeignCurrencyTransaction, ForeignCurrency


class ForeignCurrencyCreationForm(ModelForm):
    class Meta:
        model = ForeignCurrency
        fields = []


class ForeignCurrencyTransactionCreationForm(ModelForm):
    class Meta:
        model = ForeignCurrencyTransaction
        fields = [
            'transaction_date',
            'transaction_type',
            'amount',
            'exchange_rate',
            'note',
        ]

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }

