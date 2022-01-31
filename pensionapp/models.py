from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from masterinfoapp.models import PensionMaster
from portfolioapp.models import Portfolio


class Pension(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pension')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='pension')
    pension_master = models.ForeignKey(PensionMaster, on_delete=models.CASCADE, related_name='pension_master')
    total_amount = models.FloatField(default=0, null=False)
    net_paid_amount = models.FloatField(default=0, null=False)
    total_paid_amount = models.FloatField(default=0, null=False)
    total_received_amount = models.FloatField(default=0, null=False)
    total_cash_amount = models.FloatField(default=0, null=False)
    total_profit_amount = models.FloatField(default=0, null=False)
    rate_of_return = models.FloatField(default=0, null=False)
    current_risk_asset_ratio = models.FloatField(default=0, null=False)

    def __str__(self):
        return f'{self.pension_master.pension_name}'

    def update_statistics(self):
        self.calculate_pension_transaction_stats()
        self.refresh_from_db()
        self.calculate_pension_asset_stats()
        self.refresh_from_db()

    def calculate_pension_transaction_stats(self):
        queryset_pension_transaction = PensionTransaction.objects.filter(pension=self.pk)
        target_pension = Pension.objects.filter(pk=self.pk)
        total_paid_amount = 0
        total_received_amount = 0
        for transaction in queryset_pension_transaction:
            if transaction.transaction_type == 'PAY':
                total_paid_amount += transaction.amount
            elif transaction.transaction_type == 'RECEIVE':
                total_received_amount += transaction.amount
        target_pension.update(total_paid_amount=total_paid_amount)
        target_pension.update(total_received_amount=total_received_amount)
        target_pension.update(net_paid_amount=total_paid_amount-total_received_amount)
        return

    def calculate_pension_asset_stats(self):
        queryset_pension_assets = self.pension_asset.all()
        target_pension = Pension.objects.filter(pk=self.pk)
        total_amount = 0
        cash_not_used = self.net_paid_amount
        total_cash_amount = 0
        total_profit_amount = 0
        rate_of_return = 0
        current_risk_asset_ratio = 0

        for pension_asset in queryset_pension_assets:
            total_amount += pension_asset.total_amount

            total_cash_amount += pension_asset.total_realized_profit_amount
            total_cash_amount += pension_asset.total_dividend_amount
            cash_not_used -= pension_asset.average_purchase_price_fifo * pension_asset.quantity

            total_profit_amount += pension_asset.total_realized_profit_amount
            total_profit_amount += pension_asset.total_dividend_amount
            total_profit_amount += pension_asset.total_valuation_profit_amount_fifo

        total_cash_amount += cash_not_used
        target_pension.update(total_amount=total_amount)
        target_pension.update(total_cash_amount=total_cash_amount)
        target_pension.update(total_profit_amount=total_profit_amount)

        return


PENSION_TRANSACTION_TYPES = (
    ('PAY', '납입'),
    ('RECEIVE', '수령'),
)


class PensionTransaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pension_transaction')
    pension = models.ForeignKey(Pension, on_delete=models.CASCADE, related_name='pension_transaction')
    transaction_type = models.CharField(max_length=20, choices=PENSION_TRANSACTION_TYPES, null=False)
    amount = models.FloatField(default=0, null=False)
    transaction_date = models.DateTimeField(null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)