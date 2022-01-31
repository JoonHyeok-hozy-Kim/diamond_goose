from typing import Iterable

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Q

from masterinfoapp.models import AssetMaster
from pensionapp.models import Pension
from portfolioapp.models import Portfolio


class ListField(models.TextField):
    """
    A custom Django field to represent lists as comma separated strings
    """

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['token'] = self.token
        return name, path, args, kwargs

    def to_python(self, value):

        class SubList(list):
            def __init__(self, token, *args):
                self.token = token
                super().__init__(*args)

            def __str__(self):
                return self.token.join(self)

        if isinstance(value, list):
            return value
        if value is None:
            return SubList(self.token)
        return SubList(self.token, value.split(self.token))

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return
        assert(isinstance(value, Iterable))
        return self.token.join(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class Asset(models.Model):
    asset_master = models.ForeignKey(AssetMaster, on_delete=models.PROTECT, related_name='asset_master')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    quantity = models.FloatField(default=0, null=False)
    trade_stack_for_fifo = ListField(null=True)
    total_amount = models.FloatField(default=0, null=False)
    total_realized_profit_amount = models.FloatField(default=0, null=False)
    total_dividend_amount = models.FloatField(default=0, null=False)
    average_purchase_price_mv = models.FloatField(default=0, null=False)
    average_purchase_price_fifo = models.FloatField(default=0, null=False)
    total_valuation_profit_amount_mv = models.FloatField(default=0, null=False)
    total_valuation_profit_amount_fifo = models.FloatField(default=0, null=False)
    rate_of_return_mv = models.FloatField(default=0, null=False)
    rate_of_return_fifo = models.FloatField(default=0, null=False)

    def update_statistics(self):
        if self.asset_master.asset_type == 'CRYPTO':
            self.update_from_upbit()
        else:
            self.calculate_from_transaction()
        self.refresh_from_db()

    def calculate_from_transaction(self):

        query = Q(transaction_type='BUY')
        query.add(Q(transaction_type='SELL'), Q.OR)
        query.add(Q(transaction_type='DIVIDEND'), Q.OR)
        query.add(Q(transaction_type='SPLIT'), Q.OR)
        query.add(Q(applied_flag=False), Q.AND)

        queryset_transactions = self.transaction.filter(query).order_by('transaction_date')
        target_asset_instance = Asset.objects.filter(pk=self.pk)

        temp_quantity = 0
        trade_stack = []
        total_realized_profit_amount = 0
        total_dividend_amount = 0
        average_purchase_price_mv = 0
        for transaction in queryset_transactions:
            if transaction.transaction_type == 'BUY':
                # trade_stack creation
                for i in range(int(transaction.quantity)):
                    trade_stack.append(transaction.price)

                # MV calculation
                if temp_quantity == 0:
                    average_purchase_price_mv = transaction.price
                else:
                    average_purchase_price_mv = (average_purchase_price_mv * temp_quantity + transaction.price * transaction.quantity) / (temp_quantity + transaction.quantity)

                # quantity calculation
                temp_quantity += transaction.quantity

            elif transaction.transaction_type == 'SELL':
                # quantity calculation
                temp_quantity -= transaction.quantity

                # trade_stack creation
                for i in range(int(transaction.quantity)):
                    try:
                        initial_purchase_price = trade_stack.pop(0)
                        total_realized_profit_amount += (transaction.price - initial_purchase_price)
                    except Exception as trade_stack_sell_pop:
                        print('Asset-calculate_from_transaction-trade_stack_sell_pop error : {}'.format(trade_stack_sell_pop))
                        continue

            elif transaction.transaction_type == 'DIVIDEND':
                total_dividend_amount += transaction.dividend_amount

            elif transaction.transaction_type == 'SPLIT':
                temp_quantity *= transaction.split_ratio_one_to_N
                temp_quantity = round(temp_quantity)
                average_purchase_price_mv /= transaction.split_ratio_one_to_N

                new_stack = []
                index = 0
                temp_price = 0
                for trade in trade_stack:
                    if transaction.split_ratio_one_to_N > 1:
                        for i in range(int(transaction.split_ratio_one_to_N)):
                            new_stack.append(trade/transaction.split_ratio_one_to_N)
                    elif transaction.split_ratio_one_to_N < 1:
                        index += 1
                        temp_price += trade
                        if index%round(pow(transaction.split_ratio_one_to_N, -1)) == 0:
                            new_stack.append(temp_price)
                            temp_price = 0
                trade_stack = new_stack


        final_quantity = temp_quantity

        target_asset_instance.update(quantity=final_quantity)
        target_asset_instance.update(total_amount=final_quantity*self.asset_master.current_price)
        target_asset_instance.update(total_realized_profit_amount=total_realized_profit_amount)
        target_asset_instance.update(total_dividend_amount=total_dividend_amount)

        # Moving Average Series Calculation
        target_asset_instance.update(average_purchase_price_mv=average_purchase_price_mv)
        total_valuation_profit_amount_mv = (self.asset_master.current_price - average_purchase_price_mv) * final_quantity
        target_asset_instance.update(total_valuation_profit_amount_mv=total_valuation_profit_amount_mv)
        rate_of_return_mv = 0
        if average_purchase_price_mv > 0 and final_quantity > 0:
            rate_of_return_mv = (self.asset_master.current_price - average_purchase_price_mv) / average_purchase_price_mv
        target_asset_instance.update(rate_of_return_mv=rate_of_return_mv)

        # FIFO Series Calculation
        average_purchase_price_fifo = 0
        total_valuation_profit_amount_fifo = 0
        rate_of_return_fifo = 0
        if len(trade_stack) > 0:
            fifo_sum = 0
            for trade in trade_stack:
                fifo_sum += trade
            average_purchase_price_fifo = fifo_sum/final_quantity
            total_valuation_profit_amount_fifo = (self.asset_master.current_price - average_purchase_price_fifo) * final_quantity
            rate_of_return_fifo = (self.asset_master.current_price - average_purchase_price_fifo) / average_purchase_price_fifo
        target_asset_instance.update(average_purchase_price_fifo=average_purchase_price_fifo)
        target_asset_instance.update(total_valuation_profit_amount_fifo=total_valuation_profit_amount_fifo)
        target_asset_instance.update(rate_of_return_fifo=rate_of_return_fifo)

    def update_from_upbit(self):
        import jwt
        import uuid
        import hashlib
        from urllib.parse import urlencode
        import requests

        try:
            from diamond_goose.settings.local import UPBIT_ACCESS_KEY as access_key_local, UPBIT_SECRET_KEY as secret_key_local
            if access_key_local:
                access_key = access_key_local
                secret_key = secret_key_local
        except:
            from diamond_goose.settings.deploy import UPBIT_ACCESS_KEY as access_key_deploy, UPBIT_SECRET_KEY as secret_key_deploy
            access_key = access_key_deploy
            secret_key = secret_key_deploy

        server_url = "https://api.upbit.com"

        market = 'KRW-'
        market += self.asset_master.ticker
        query = {
            'market': market,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)

        # My Account Data in Json
        my_account = res.json()['ask_account']
        my_balance = float(my_account['balance'])
        my_avg_buy_price = float(my_account['avg_buy_price'])

        asset = Asset.objects.filter(pk=self.pk)
        asset.update(quantity=my_balance)
        total_amount = my_balance * self.asset_master.current_price
        asset.update(total_amount=total_amount)
        asset.update(average_purchase_price_mv=my_avg_buy_price)
        asset.update(average_purchase_price_fifo=my_avg_buy_price)
        rate_of_return = 0
        if my_avg_buy_price > 0:
            rate_of_return = (self.asset_master.current_price-my_avg_buy_price)/my_avg_buy_price
        asset.update(rate_of_return_mv=rate_of_return)
        asset.update(rate_of_return_fifo=rate_of_return)



class PensionAsset(Asset):
    pension = models.ForeignKey(Pension, on_delete=models.CASCADE, related_name='pension_asset')


class MinValueFloat(models.FloatField):
    def __init__(self, min_value=None, *args, **kwargs):
        self.min_value = min_value
        super(MinValueFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(MinValueFloat, self).formfield(**defaults)


TRANSACTION_TYPE_CHOICES = (
    ('BUY', '매수'),
    ('SELL', '매도'),
    ('DIVIDEND', '배당금'),
    ('SPLIT', '액면분할'),
)


class AssetTransaction(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transaction')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, null=False)
    quantity = MinValueFloat(min_value=0, default=0, null=False)
    price = MinValueFloat(min_value=0, default=0, null=False)
    dividend_amount = MinValueFloat(default=0, min_value=0, null=True)
    split_ratio_one_to_N = MinValueFloat(default=1, min_value=0, null=False)
    transaction_fee = MinValueFloat(min_value=0, default=0, null=True)
    transaction_tax = models.FloatField(default=0, null=True)
    note = models.CharField(max_length=100, default='-', null=True)
    applied_flag = models.BooleanField(default=False, null=False)
    transaction_date = models.DateTimeField(null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)