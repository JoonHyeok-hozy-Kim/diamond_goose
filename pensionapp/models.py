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
    total_paid_amount = models.FloatField(default=0, null=False)
    total_cash_amount = models.FloatField(default=0, null=False)
    total_profit_amount = models.FloatField(default=0, null=False)
    rate_of_return = models.FloatField(default=0, null=False)
    current_risk_asset_ratio = models.FloatField(default=0, null=False)

    def __str__(self):
        return f'{self.pension_master.pension_name}'

    def update_parameters(self):
        self.calculate_pension_transaction_stats()
        self.refresh_from_db()
        self.calculate_pension_asset_stats()
        self.refresh_from_db()

    def calculate_pension_transaction_stats(self):
        # pension_transaction_query = self.pension_transaction.all()
        # new_total_paid_amount = 0
        # for transaction in pension_transaction_query:
        #     if transaction.transaction_type == 'PAY':
        #         new_total_paid_amount += transaction.amount
        #     else:
        #         new_total_paid_amount -= transaction.amount
        #
        # pension = Pension.objects.filter(pk=self.pk)
        # pension.update(total_paid_amount=new_total_paid_amount)
        # return new_total_paid_amount
        return

    def calculate_pension_asset_stats(self):
        # queryset_pension_asset = self.pension_asset.all()
        # total_asset_purchase_amount = 0
        # total_asset_dividend_amount = 0
        # total_current_value = 0
        # current_risk_asset_ratio = 0
        # current_risk_asset_amount = 0
        #
        # for pension_asset in queryset_pension_asset:
        #     total_asset_purchase_amount += pension_asset.average_purchase_price_mv * pension_asset.quantity
        #     total_asset_dividend_amount += pension_asset.total_dividend_amount
        #     total_current_value += pension_asset.total_amount
        #     if not pension_asset.asset.pension_non_risk_asset_flag:
        #         current_risk_asset_amount += pension_asset.total_amount
        #
        # total_cash_amount = self.total_paid_amount + total_asset_dividend_amount - total_asset_purchase_amount
        # total_current_value += total_cash_amount
        # if current_risk_asset_amount > 0:
        #     current_risk_asset_ratio = current_risk_asset_amount / total_current_value
        #
        # pension = Pension.objects.filter(pk=self.pk)
        # pension.update(total_cash_amount=total_cash_amount)
        # pension.update(total_current_value=total_current_value)
        # pension.update(current_risk_asset_ratio=current_risk_asset_ratio)
        #
        # return {'total_current_value': total_current_value, 'total_cash_amount': total_cash_amount}
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