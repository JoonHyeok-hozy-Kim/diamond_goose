import json
import requests
from django.db import models
import yfinance as yf

# Create your models here.
class CurrencyMaster(models.Model):
    currency_code = models.CharField(max_length=10, null=False)
    currency_name = models.CharField(max_length=100, null=False)
    currency_sign = models.CharField(max_length=10, null=True)
    currency_national_flag = models.ImageField(upload_to='currencymaster/', null=True)

    def __str__(self):
        result_list = [self.currency_name]
        if self.currency_sign:
            result_list.append('(')
            result_list.append(self.currency_sign)
            result_list.append(')')
        return ''.join(result_list)


ASSET_TYPES = (
    ('EQUITY', 'Equity'),
    ('GUARDIAN', 'Guardian'),
    ('REITS', 'Reits'),
    ('PENSION_ASSET', 'Pension Asset'),
    ('CRYPTO', 'Crypto Asset'),
)

MARKET_CHOICES = (
    ('KSE', 'Korean Stock Exchange(KSE)'),
    ('NASDAQ', 'NASDAQ'),
    ('NYSE', 'NewYork Stock Exchange(NYSE)'),
    ('NA', 'Not Applicable')
)


class AssetMaster(models.Model):
    asset_type = models.CharField(max_length=100, choices=ASSET_TYPES, null=True)
    market = models.CharField(max_length=100, choices=MARKET_CHOICES, null=True)
    ticker = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=200, null=True)
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.PROTECT, null=False, related_name='asset_master')
    image = models.ImageField(upload_to='assetmaster/', default='static/images/diamond_goose_logo_mk1.png', null=False)

    current_price = models.FloatField(default=0, null=False)
    pension_asset_flag = models.BooleanField(default=False, null=False)
    pension_risk_asset_flag = models.BooleanField(default=False, null=False)

    def update_current_price(self):
        yfinance_markets = ['NASDAQ', 'NYSE', 'KSE']
        result_current_price = 0

        if self.market in yfinance_markets:
            ticker = self.ticker
            if self.market == 'KSE':
                ticker += '.KS'
            try:
                ticker_data = yf.Ticker(ticker)
                today_ticker_data = ticker_data.history(period='1d')

                if self.market == 'KSE':
                    result_current_price = round(today_ticker_data['Close'][0])
                else:
                    result_current_price = round(today_ticker_data['Close'][0], 2)
            except Exception as identifier:
                print('[Exception] Asset Model, update_current_price : ', identifier)

        else:
            if self.asset_type == 'CRYPTO':
                url_list = ['https://api.upbit.com/v1/candles/minutes/1?market=']
                url_list.append(self.currency.currency_code)
                url_list.append('-')
                url_list.append(self.ticker)
                url_list.append('&count=1')
                url = ''.join(url_list)
                headers = {"Accept": "application/json"}
                response = requests.request("GET", url, headers=headers)
                dict_result = json.loads(response.text[1:-1])
                result_current_price = round(float(dict_result['opening_price']), 2)

        asset = AssetMaster.objects.filter(pk=self.pk)
        asset.update(current_price=result_current_price)

        return result_current_price


class PensionMaster(models.Model):
    pension_type = models.CharField(max_length=100, null=False)
    pension_name = models.CharField(max_length=100, null=False)
    risk_ratio_force_flag = models.BooleanField(default=False, null=False)
    risk_ratio = models.FloatField(default=0, null=False)

    def __str__(self):
        return '{}'.format(self.pension_name)
