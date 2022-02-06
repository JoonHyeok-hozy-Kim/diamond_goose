import json
import requests
from django.db import models
import yfinance as yf
import investpy as ip

# Create your models here.
class CurrencyMaster(models.Model):
    currency_code = models.CharField(max_length=10, null=False)
    currency_name = models.CharField(max_length=100, null=False)
    currency_sign = models.CharField(max_length=10, null=True)
    currency_national_flag = models.ImageField(upload_to='currencymaster/', null=True)
    country = models.CharField(max_length=100, null=True)

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
    etf_flag = models.BooleanField(default=False, null=True)
    market = models.CharField(max_length=100, choices=MARKET_CHOICES, null=True)
    ticker = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=200, null=True)
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.PROTECT, null=False, related_name='asset_master')
    image = models.ImageField(upload_to='assetmaster/', default='static/images/diamond_goose_logo_mk1.png', null=False)

    current_price = models.FloatField(default=0, null=False)
    pension_asset_flag = models.BooleanField(default=False, null=False)
    pension_risk_asset_flag = models.BooleanField(default=False, null=False)

    def update_statistics(self):
        self.update_current_price()
        self.refresh_from_db()

    def update_current_price(self):
        target_asset_master = AssetMaster.objects.filter(pk=self.pk)
        yfinance_markets = ['NASDAQ', 'NYSE', 'KSE']

        if self.asset_type == 'CRYPTO':
            result = self.get_from_upbit()
        elif self.market in yfinance_markets:
            try:
                result = self.get_from_yfinance()
            except Exception as yfinance_exception:
                print('update_current_price - yfinance : {}'.format(yfinance_exception))
                result = self.get_from_investpy(target_asset_master)
        else:
            result = self.get_from_investpy(target_asset_master)

        if result:
            print('{}, current_price : {} ({})'.format(self.name, result['current_price'], result['data_source']))
            target_asset_master.update(current_price=result['current_price'])

    def get_from_upbit(self):
        url_list = ['https://api.upbit.com/v1/candles/minutes/1?market=']
        url_list.append(self.currency.currency_code)
        url_list.append('-')
        url_list.append(self.ticker)
        url_list.append('&count=1')
        url = ''.join(url_list)
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers)
        dict_result = json.loads(response.text[1:-1])
        current_price = round(float(dict_result['trade_price']), 2)
        return {'current_price': current_price, 'data_source': 'upbit'}

    def get_from_yfinance(self):
        ticker = self.ticker
        if self.market == 'KSE':
            ticker += '.KS'
        try:
            ticker_data = yf.Ticker(ticker)
            today_ticker_data = ticker_data.history(period='1d')

            if self.market == 'KSE':
                current_price = round(today_ticker_data['Close'][0])
            else:
                current_price = round(today_ticker_data['Close'][0], 2)
        except Exception as get_from_yfinance:
            print('get_from_yfinance : {}'.format(get_from_yfinance))
            return

        return {'current_price': current_price, 'data_source': 'yfinance'}


    def get_from_investpy(self, target_asset_master):
        current_price_json = None
        if self.etf_flag:
            try:
                current_price_json = ip.get_etf_information(self.name, self.currency.country, True)
            except Exception as get_etf_information:
                print('get_from_investpy - get_etf_information : {}'.format(get_etf_information))
                try:
                    search_etf = json.loads(ip.search_etfs('symbol', self.ticker).to_json())
                    index = 0
                    target_index = -1
                    for i in search_etf['country']:
                        if search_etf['country'][str(index)] == self.currency.country.lower() and search_etf['symbol'][str(index)] == self.ticker:
                            target_index = index
                        index += 1
                    if target_index >= 0:
                        target_etf_name = search_etf['name'][str(target_index)]
                        target_asset_master.update(name=target_etf_name)
                        try:
                            current_price_json = ip.get_etf_information(target_etf_name, self.currency.country, True)
                            print('ETF AFTER NAME SEARCH')
                        except Exception as get_etf_exception:
                            print('get_from_investpy - get_etf_information : {}'.format(get_etf_exception))

                except Exception as search_etfs:
                    print('get_from_investpy - search_etfs : {}'.format(search_etfs))
                    return
        else:
            try:
                current_price_json = ip.get_stock_information(self.ticker, self.currency.country, True)
            except Exception as get_stock_information:
                print('get_from_investpy - get_stock_information : {}'.format(get_stock_information))
                return

        if current_price_json:
            return {'current_price': current_price_json['Prev. Close'], 'data_source': 'investpy'}


class PensionMaster(models.Model):
    pension_type = models.CharField(max_length=100, null=False)
    pension_name = models.CharField(max_length=100, null=False)
    risk_ratio_force_flag = models.BooleanField(default=False, null=False)
    risk_ratio = models.FloatField(default=0, null=False)

    def __str__(self):
        return '{}'.format(self.pension_name)
