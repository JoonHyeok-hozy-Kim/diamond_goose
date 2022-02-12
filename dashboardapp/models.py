from django.contrib.auth.models import User
from django.db import models
from django import utils

# Create your models here.
from masterinfoapp.models import CurrencyMaster


class Dashboard(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='dashboard')
    main_currency = models.ForeignKey(CurrencyMaster, on_delete=models.PROTECT, related_name='main_currency')
    initial_date = models.DateTimeField(default=utils.timezone.now, null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)


# class HistoryCapture(models.Model):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_capture')
#     dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='history_capture')
#     capture_date = models.DateTimeField(default=utils.timezone.now, null=False)
#
#     total_asset_amount = models.FloatField(default=0, null=True)
#     total_liquidity_amount = models.FloatField(default=0, null=True)
#     total_investment_amount = models.FloatField(default=0, null=True)
#
#     total_debt_amount = models.FloatField(default=0, null=True)
#     debt_amount_short_term = models.FloatField(default=0, null=True)
#     debt_amount_long_term = models.FloatField(default=0, null=True)
#
#     net_capital_amount = models.FloatField(default=0, null=True)