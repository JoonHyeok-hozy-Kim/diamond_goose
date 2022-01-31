from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class TempTransaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temp_transaction', null=False)

    data_source = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20)
    transaction_type = models.CharField(max_length=100)

    ticker = models.CharField(max_length=20)
    pension_type = models.CharField(max_length=20)
    currency = models.CharField(max_length=20)

    quantity = models.FloatField(default=0)
    price = models.FloatField(default=0)
    exchange_rate = models.FloatField(default=0)
    transaction_fee = models.FloatField(default=0)
    transaction_tax = models.FloatField(default=0)
    split_ratio_one_to_N = models.FloatField(default=0)

    transaction_date = models.DateTimeField()

    applied_flag = models.BooleanField(default=False, null=False)
    applied_date = models.DateTimeField(null=True)

    creation_date = models.DateTimeField(auto_now=True, null=False)
    last_update_date = models.DateTimeField(auto_now_add=True, null=False)