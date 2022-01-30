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