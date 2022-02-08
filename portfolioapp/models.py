from django.contrib.auth.models import User
from django.db import models

from dashboardapp.models import Dashboard
from exchangeapp.models import ForeignCurrency
from masterinfoapp.models import CurrencyMaster


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

    def update_statistics(self, price_update=False):
        if price_update:
            self.update_current_value(price_update=True)
        else:
            self.update_current_value()
        self.refresh_from_db()

    def asset_value_exchange(self, asset):
        currency_code_pk = asset.asset_master.currency.pk
        target_currency_master = CurrencyMaster.objects.get(pk=currency_code_pk)
        target_foreign_currency = ForeignCurrency.objects.get(dashboard=self.dashboard.pk,
                                                              currency_master=target_currency_master.pk)
        result = {
            'current_value_exchange_market': asset.total_amount * target_foreign_currency.current_exchange_rate,

            'profit_mv_exchange_market': asset.total_valuation_profit_amount_mv * target_foreign_currency.current_exchange_rate,
            'profit_mv_exchange_mv': asset.total_valuation_profit_amount_mv * target_foreign_currency.accumulated_exchange_rate_mv,
            'profit_mv_exchange_fifo': asset.total_valuation_profit_amount_mv * target_foreign_currency.accumulated_exchange_rate_fifo,

            'profit_fifo_exchange_market': asset.total_valuation_profit_amount_fifo * target_foreign_currency.current_exchange_rate,
            'profit_fifo_exchange_mv': asset.total_valuation_profit_amount_fifo * target_foreign_currency.accumulated_exchange_rate_mv,
            'profit_fifo_exchange_fifo': asset.total_valuation_profit_amount_fifo * target_foreign_currency.accumulated_exchange_rate_fifo,
        }

        return result

    def update_current_value(self, price_update=False):
        target_portfolio = Portfolio.objects.filter(pk=self.pk)
        current_value_exchange_market = 0
        profit_mv_exchange_market = 0
        profit_mv_exchange_mv = 0
        profit_mv_exchange_fifo = 0
        profit_fifo_exchange_market = 0
        profit_fifo_exchange_mv = 0
        profit_fifo_exchange_fifo = 0

        # Assets
        from assetapp.models import Asset
        queryset_assets = Asset.objects.filter(portfolio=self.pk)
        for asset in queryset_assets:
            if price_update:
                asset.update_statistics()
            if asset.asset_master.currency.currency_code == self.dashboard.main_currency.currency_code:
                current_value_exchange_market += asset.total_amount

                profit_mv_exchange_market += asset.total_valuation_profit_amount_mv
                profit_mv_exchange_mv += asset.total_valuation_profit_amount_mv
                profit_mv_exchange_fifo += asset.total_valuation_profit_amount_mv

                profit_fifo_exchange_market += asset.total_valuation_profit_amount_fifo
                profit_fifo_exchange_mv += asset.total_valuation_profit_amount_fifo
                profit_fifo_exchange_fifo += asset.total_valuation_profit_amount_fifo

            else:
                profit_dict = self.asset_value_exchange(asset)
                current_value_exchange_market += profit_dict['current_value_exchange_market']

                profit_mv_exchange_market += profit_dict['profit_mv_exchange_market']
                profit_mv_exchange_mv += profit_dict['profit_mv_exchange_mv']
                profit_mv_exchange_fifo += profit_dict['profit_mv_exchange_fifo']

                profit_fifo_exchange_market += profit_dict['profit_fifo_exchange_market']
                profit_fifo_exchange_mv += profit_dict['profit_fifo_exchange_mv']
                profit_fifo_exchange_fifo += profit_dict['profit_fifo_exchange_fifo']

        # # Pension Assets
        # from assetapp.models import PensionAsset
        # queryset_pension_assets = PensionAsset.objects.filter(portfolio=self.pk)
        # print('queryset_pension_assets')
        # for pension_asset in queryset_pension_assets:
        #     pension_asset.update_statistics()
        #     if pension_asset.asset_master.currency.currency_code == self.dashboard.main_currency.currency_code:
        #         current_value_exchange_market += asset.total_amount
        #
        #         profit_mv_exchange_market += asset.total_valuation_profit_amount_mv
        #         profit_mv_exchange_mv += pension_asset.total_valuation_profit_amount_mv
        #         profit_mv_exchange_fifo += pension_asset.total_valuation_profit_amount_mv
        #
        #         profit_fifo_exchange_market += asset.total_valuation_profit_amount_fifo
        #         profit_fifo_exchange_mv += pension_asset.total_valuation_profit_amount_fifo
        #         profit_fifo_exchange_fifo += pension_asset.total_valuation_profit_amount_fifo
        #     else:
        #         profit_dict = self.asset_value_exchange(pension_asset)
        #         current_value_exchange_market += profit_dict['current_value_exchange_market']
        #
        #         profit_mv_exchange_market += profit_dict['profit_mv_exchange_market']
        #         profit_mv_exchange_mv += profit_dict['profit_mv_exchange_mv']
        #         profit_mv_exchange_fifo += profit_dict['profit_mv_exchange_fifo']
        #
        #         profit_fifo_exchange_market += profit_dict['profit_fifo_exchange_market']
        #         profit_fifo_exchange_mv += profit_dict['profit_fifo_exchange_mv']
        #         profit_fifo_exchange_fifo += profit_dict['profit_fifo_exchange_fifo']

        # Pension Cash Amount
        from pensionapp.models import Pension
        queryset_pensions = Pension.objects.filter(portfolio=self.pk)
        for pension in queryset_pensions:
            if pension.currency.currency_code == self.dashboard.main_currency.currency_code:
                current_value_exchange_market += pension.total_cash_amount
            else:
                target_foreign_currency = ForeignCurrency.objects.get(currency_master=pension.currency)
                current_value_exchange_market += pension.total_cash_amount * target_foreign_currency.current_exchange_rate

        current_value = current_value_exchange_market
        target_portfolio.update(current_value=current_value)

        # 2 options for capital_gain
        capital_gain = profit_mv_exchange_market
        # capital_gain = profit_fifo_exchange_market
        target_portfolio.update(capital_gain=capital_gain)


        # 4 options for capital_gain_foreign_exchange_adjusted
        capital_gain_foreign_exchange_adjusted = profit_mv_exchange_mv
        # capital_gain_foreign_exchange_adjusted = profit_mv_exchange_fifo
        # capital_gain_foreign_exchange_adjusted = profit_fifo_exchange_mv
        # capital_gain_foreign_exchange_adjusted = profit_fifo_exchange_fifo
        target_portfolio.update(capital_gain_foreign_exchange_adjusted=capital_gain_foreign_exchange_adjusted)


        if current_value > 0:
            rate_of_return = capital_gain/current_value
            target_portfolio.update(rate_of_return=rate_of_return)
            rate_of_return_foreign_exchange_adjusted = capital_gain_foreign_exchange_adjusted/current_value
            target_portfolio.update(rate_of_return_foreign_exchange_adjusted=rate_of_return_foreign_exchange_adjusted)

