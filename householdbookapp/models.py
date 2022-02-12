from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dashboardapp.models import Dashboard
from exchangeapp.models import ForeignCurrency
from masterinfoapp.models import CurrencyMaster

liquidity_type_list = (
    ('DEPOSIT', 'Bank Deposit'),
    ('CMA', "IB's CMA"),
    ('INSTALLMENT', 'Installment Saving'),
    ('VOUCHER', 'Voucher'),
    ('FOREIGN_CURRENCY', 'Foreign Currency'),
)


class Liquidity(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liquidity')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='liquidity')
    liquidity_type = models.CharField(max_length=100, choices=liquidity_type_list, null=False)
    liquidity_name = models.CharField(max_length=100, default='Liquidity', null=False)
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.CASCADE, related_name='liquidity')
    amount = models.FloatField(default=0, null=False)
    amount_exchanged = models.FloatField(default=0, null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_statistics(self):
        self.amount_exchanged_calculation()
        self.refresh_from_db()

    def amount_exchanged_calculation(self):
        queryset_my_foreign_currencies = ForeignCurrency.objects.filter(owner=self.owner,
                                                                        dashboard=self.dashboard)
        target_liquidity = Liquidity.objects.filter(pk=self.pk)
        for foreign_currency in queryset_my_foreign_currencies:
            if self.currency == foreign_currency.currency_master:
                amount_exchanged = self.amount * foreign_currency.current_exchange_rate
                target_liquidity.update(amount_exchanged=amount_exchanged)
                return
        target_liquidity.update(amount_exchanged=self.amount)