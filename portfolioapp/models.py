from django.contrib.auth.models import User
from django.db import models
from dashboardapp.models import Dashboard


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='portfolio')
    current_value = models.FloatField(default=0, null=False)
    capital_gain = models.FloatField(default=0, null=False)
    capital_gain_foreign_exchange_adjusted = models.FloatField(default=0, null=False)
    rate_of_return = models.FloatField(default=0, null=False)
    rate_of_return_foreign_exchange_adjusted = models.FloatField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def asset_value_exchange(self):
        None

    def update_current_value(self):
        None