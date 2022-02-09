import json
import time
from datetime import timedelta

import requests
import investpy as ip

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dashboardapp.models import Dashboard
from masterinfoapp.models import CurrencyMaster


class ForeignCurrency(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='foreign_currency', null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foreign_currency', null=False)
    currency_master = models.ForeignKey(CurrencyMaster, on_delete=models.CASCADE, related_name='foreign_currency', null=False)
    current_amount = models.FloatField(default=0, null=False)
    current_exchange_rate = models.FloatField(default=0, null=False)
    accumulated_exchange_rate_mv = models.FloatField(default=0, null=False)
    accumulated_exchange_rate_fifo = models.FloatField(default=0, null=False)
    rate_of_return_mv = models.FloatField(default=0, null=False)
    rate_of_return_fifo = models.FloatField(default=0, null=False)
    total_realized_profit = models.FloatField(default=0, null=False)

    def update_statistics(self):
        self.get_current_exchange_rate()
        self.refresh_from_db()
        self.calculate_statistics()
        self.refresh_from_db()

    def get_current_exchange_rate(self):
        import datetime

        # url_list = ['https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?']
        # url_list.append('authkey=')
        # try:
        #     from diamond_goose.settings.local import EXIM_BANK_API_KEY as key_local
        #     if key_local:
        #         url_list.append(key_local)
        # except:
        #     from diamond_goose.settings.deploy import EXIM_BANK_API_KEY as key_deploy
        #     url_list.append(key_deploy)
        # url_list.append('&searchdate=')
        #
        # today = datetime.datetime.today()
        # while True:
        #     url_list.append(today.strftime("%Y%m%d"))
        #     url_list.append('&data=AP01')
        #
        #     url = ''.join(url_list)
        #     headers = {"Accept": "application/json"}
        #     response = requests.request("GET", url, headers=headers)
        #     dict_result = json.loads(response.text)
        #
        #     if dict_result:
        #         print('EXIM Bank url : {}'.format(url))
        #         break;
        #     else:
        #         today -= datetime.timedelta(days=1)
        #         url_list.pop(-1)
        #         url_list.pop(-1)
        #
        # exchange_rate = self.current_exchange_rate
        #
        # for result in dict_result:
        #     if result['cur_unit'][0:3] == self.currency_master.currency_code:
        #         exchange_rate_char_list = []
        #         for char in result['deal_bas_r']:
        #             if char != ',':
        #                 exchange_rate_char_list.append(char)
        #
        #         exchange_rate = round(float(''.join(exchange_rate_char_list)), 2)
        #
        #         if len(result['cur_unit']) > 3:
        #             power_list = []
        #             for char in result['cur_unit']:
        #                 if char.isnumeric():
        #                     power_list.append(char)
        #             power = int(''.join(power_list))
        #             exchange_rate /= power
        #
        #         foreign_currency = ForeignCurrency.objects.filter(pk=self.pk)
        #         foreign_currency.update(current_exchange_rate=exchange_rate)

        currency_cross_list = [
            self.currency_master.currency_code,
            '/',
            self.dashboard.main_currency.currency_code,
        ]
        currency_cross = ''.join(currency_cross_list)
        current_exchange_rate = None
        try:
            current_exchange_rate_json = json.loads(ip.get_currency_cross_information(currency_cross, True))
            current_exchange_rate = (current_exchange_rate_json['ask'] + current_exchange_rate_json['bid'])/2
        except Exception as currency_rate_search:
            print('exchangeapp - get_current_exchange_rate - get_currency_cross_information error : {}'.format(currency_rate_search))

            try:
                current_exchange_rate_json = json.loads(ip.get_currency_cross_recent_data(currency_cross, True))
                current_exchange_rate = current_exchange_rate_json['recent'][-1]['close']
                print(' -> Got from recent_data instead : {}'.format(current_exchange_rate))
            except Exception as currency_rate_search_recent:
                print('exchangeapp - get_current_exchange_rate - currency_rate_search_recent error : {}'.format(currency_rate_search_recent))

        if current_exchange_rate:
            foreign_currency = ForeignCurrency.objects.filter(pk=self.pk)
            foreign_currency.update(current_exchange_rate=current_exchange_rate)

        return current_exchange_rate

    def calculate_statistics(self):
        from django.db.models import Q
        query = Q(transaction_type='BUY')
        query.add(Q(transaction_type='SELL'),Q.OR)
        query.add(Q(amount__gt=0),Q.AND)

        queryset_transactions = self.transaction.filter(query)
        target_foreign_currency = ForeignCurrency.objects.filter(pk=self.pk)
        current_amount = 0
        trade_stack = []
        accumulated_exchange_rate_mv = 0
        rate_of_return_mv = 0
        total_realized_profit = 0

        history_start_date = None
        history_end_date = None
        history_target_pk_list = []

        idx = -1
        for transaction in queryset_transactions:
            idx += 1
            if transaction.transaction_type == 'BUY':
                # trade_stack append
                trade_stack.append({'exchange_rate': transaction.exchange_rate, 'amount': transaction.amount})

                # MV caluclation
                if idx == 0:
                    accumulated_exchange_rate_mv = transaction.exchange_rate
                else:
                    accumulated_exchange_rate_mv = (accumulated_exchange_rate_mv * current_amount + transaction.exchange_rate * transaction.amount) / (current_amount + transaction.amount)

                # current_amount calculation
                current_amount += transaction.amount

            elif transaction.transaction_type == 'SELL':
                # trade_stack pop
                selling_amount = transaction.amount
                while selling_amount > 0:
                    if selling_amount > trade_stack[0]['amount']:
                        target_purchase = trade_stack.pop(0)
                        total_realized_profit += (transaction.exchange_rate - target_purchase['exchange_rate']) * target_purchase['amount']
                        selling_amount -= target_purchase['amount']
                    else:
                        target_purchase = trade_stack[0]
                        total_realized_profit += (transaction.exchange_rate - target_purchase['exchange_rate']) * target_purchase['amount']
                        target_purchase['amount'] -= selling_amount
                        break;

                # current_amount calculation
                current_amount -= transaction.amount

            # Check transactions which market_closing_rate is None
            if transaction.market_closing_rate is None and history_start_date is None:
                history_start_date = transaction.transaction_date - timedelta(days=1)
                history_end_date = transaction.transaction_date
                history_target_pk_list.append(transaction.pk)
            elif transaction.market_closing_rate is None and history_start_date is not None:
                history_end_date = transaction.transaction_date
                history_target_pk_list.append(transaction.pk)

        # Insert market_closing_rate for checked transactions
        if history_start_date is not None and history_end_date is not None:
            currency_cross_list = [
                self.currency_master.currency_code,
                '/',
                self.dashboard.main_currency.currency_code,
            ]
            currency_cross = ''.join(currency_cross_list)
            market_closing_rate_json = None
            try:
                market_closing_rate_json = json.loads(ip.get_currency_cross_historical_data(currency_cross,
                                                                                            history_start_date.strftime("%d/%m/%Y"),
                                                                                            history_end_date.strftime("%d/%m/%Y"),
                                                                                            True))
                history_dict = market_closing_rate_json['historical']
            except Exception as historical_market_data:
                print('Exception for historical_market_data : {}'.format(historical_market_data))

                try:
                    currency_cross = ''.join(currency_cross_list[::-1])
                    market_closing_rate_json = json.loads(ip.get_currency_cross_historical_data(currency_cross,
                                                                                                history_start_date.strftime("%d/%m/%Y"),
                                                                                                history_end_date.strftime("%d/%m/%Y"),
                                                                                                True))
                    history_dict = market_closing_rate_json['historical']
                except Exception as historical_market_data_reverse:
                    print('Exception for historical_market_data_reverse : {}'.format(historical_market_data_reverse))

            if market_closing_rate_json is not None:
                for transaction_pk in history_target_pk_list:
                    target_transaction = ForeignCurrencyTransaction.objects.filter(pk=transaction_pk)
                    target_transaction_date = target_transaction.values('transaction_date')[0]['transaction_date'].strftime("%d/%m/%Y")
                    for dict_element in history_dict:
                        if dict_element['date'] == target_transaction_date:
                            target_transaction.update(market_closing_rate=dict_element['close'])
                            print(' - Historical market rate inserted, {} : {}'.format(target_transaction_date,
                                                                                       dict_element['close']))


        target_foreign_currency.update(current_amount=current_amount)
        target_foreign_currency.update(total_realized_profit=total_realized_profit)

        # MV Series Calculation
        target_foreign_currency.update(accumulated_exchange_rate_mv=accumulated_exchange_rate_mv)
        if accumulated_exchange_rate_mv > 0:
            rate_of_return_mv = (self.current_exchange_rate - accumulated_exchange_rate_mv) / accumulated_exchange_rate_mv
        target_foreign_currency.update(rate_of_return_mv=rate_of_return_mv)

        # FIFO Series Calculation
        accumulated_exchange_rate_fifo = 0
        rate_of_return_fifo = 0
        if len(trade_stack) > 0:
            fifo_sum = 0
            for trade in trade_stack:
                fifo_sum += trade['exchange_rate'] * trade['amount']
            accumulated_exchange_rate_fifo = fifo_sum / current_amount
            rate_of_return_fifo = (self.current_exchange_rate - accumulated_exchange_rate_fifo) / accumulated_exchange_rate_fifo
        target_foreign_currency.update(accumulated_exchange_rate_fifo=accumulated_exchange_rate_fifo)
        target_foreign_currency.update(rate_of_return_fifo=rate_of_return_fifo)

TRANSACTION_TYPE_CHOICES = (
    ('BUY', '매수'),
    ('SELL', '매도'),
)


class ForeignCurrencyTransaction(models.Model):
    foreign_currency = models.ForeignKey(ForeignCurrency, on_delete=models.CASCADE, related_name='transaction')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, null=False)
    amount = models.FloatField(default=0, null=False)
    exchange_rate = models.FloatField(default=0, null=False)
    market_closing_rate = models.FloatField(null=True)
    applied_flag = models.BooleanField(default=False, null=False)
    note = models.CharField(max_length=100, default='-', null=True)
    transaction_date = models.DateTimeField(null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)