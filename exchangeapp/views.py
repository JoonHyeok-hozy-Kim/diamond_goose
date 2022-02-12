import datetime
import json
from time import sleep

import investpy as ip
from datetime import timedelta

from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import DetailView, CreateView, ListView
from django.views.generic.edit import FormMixin, DeleteView
from pyecharts.charts import Line, Grid
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from rest_framework.views import APIView

from dashboardapp.models import Dashboard
from diamond_goose.pyecharts import json_response
from exchangeapp.forms import ForeignCurrencyCreationForm, ForeignCurrencyTransactionCreationForm
from exchangeapp.models import ForeignCurrency, ForeignCurrencyTransaction
from masterinfoapp.models import CurrencyMaster


class MyExchangeDetailView(DetailView):
    model = Dashboard
    context_object_name = 'my_dashboard'
    template_name = 'exchangeapp/myexchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MyExchangeDetailView, self).get_context_data(**kwargs)

        queryset_foreign_currencies = ForeignCurrency.objects.filter(owner=self.request.user,
                                                                    dashboard=self.object.pk)
        context.update({'queryset_foreign_currencies': queryset_foreign_currencies})
        context.update({'myexchange_detail_flag': True})

        return context


class MyExchangeCurrencyMasterListView(ListView):
    model = CurrencyMaster
    template_name = 'masterinfoapp/currencymaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyExchangeCurrencyMasterListView, self).get_context_data(**kwargs)

        query_currency_master_list = CurrencyMaster.objects.exclude(id__in=Dashboard.objects.filter(owner=self.request.user).values('main_currency_id')).exclude(id__in=ForeignCurrency.objects.filter(owner=self.request.user).values('currency_master_id')).order_by('currency_code')
        for currency_master in query_currency_master_list:
            currency_master.name = Truncator(currency_master.currency_name).chars(29)
        context.update({'query_currency_master_list': query_currency_master_list})
        context.update({'myexchange_currencymaster_list_flag': True})

        return context


class MyExchangeCurrencyMasterDetailView(DetailView, FormMixin):
    model = CurrencyMaster
    form_class = ForeignCurrencyCreationForm
    context_object_name = 'target_currency_master'
    template_name = 'template_currencymaster_detail.html'

    def get_context_data(self, **kwargs):

        context = super(MyExchangeCurrencyMasterDetailView, self).get_context_data(**kwargs)
        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'myexchange_currency_master_flag': True})

        return context


class ForeignCurrencyCreateView(CreateView):
    model = ForeignCurrency
    form_class = ForeignCurrencyCreationForm
    template_name = 'exchangeapp/foreigncurrency_create.html'

    def form_valid(self, form):
        temp_currency = form.save(commit=False)
        currency_master_pk = self.request.POST['currency_master_pk']

        temp_currency.dashboard = Dashboard.objects.get(owner=self.request.user)
        temp_currency.owner = self.request.user
        temp_currency.currency_master = CurrencyMaster.objects.get(pk=currency_master_pk)
        temp_currency.save()

        return super().form_valid(form)

    def get_success_url(self):
        target_dashboard = Dashboard.objects.get(owner=self.request.user)
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': target_dashboard.pk})


class ForeignCurrencyDeleteView(DeleteView):
    model = ForeignCurrency
    context_object_name = 'target_foreign_currency'
    template_name = 'exchangeapp/foreigncurrency_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': self.object.dashboard.pk})


class ForeignCurrencyDetailView(DetailView, FormMixin):
    model = ForeignCurrency
    context_object_name = 'target_foreign_currency'
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrency_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ForeignCurrencyDetailView, self).get_context_data(**kwargs)

        queryset_transaction_list = ForeignCurrencyTransaction.objects.filter(foreign_currency=self.object.pk).order_by("-transaction_date")
        for transaction in queryset_transaction_list:
            if transaction.market_closing_rate is None:
                transaction.market_closing_rate = '-'
        context.update({'queryset_transaction_list': queryset_transaction_list})

        line_graph_url_list = ['http://']
        ip_address = None
        try:
            from diamond_goose.settings.local import LOCAL_IP_ADDRESS
            ip_address = LOCAL_IP_ADDRESS
        except Exception as deploy_environment:
            print('Fo Chart - deploy_environment : {}'.format(deploy_environment))
            from diamond_goose.settings.deploy import DEPLOY_IP_ADDRESS
            ip_address = DEPLOY_IP_ADDRESS

        if ip_address:
            line_graph_url_list.append(ip_address)
            line_graph_url_list.append('/exchange/foreigncurrency_line_graph/')
            line_graph_url_list.append(str(self.object.pk))
            context.update({'line_graph_url': ''.join(line_graph_url_list)})

        # Update Foreign Currency Stats.
        self.object.update_statistics()

        return context


def foreign_currency_line_graph(request, foreign_currency_pk) -> Line:
    queryset_foreign_currency_transactions = ForeignCurrencyTransaction.objects.filter(foreign_currency_id=foreign_currency_pk).order_by('transaction_date')

    transaction_date_list = []
    my_exchange_rate_list = []
    market_exchange_rate_list = []
    count = 0
    for transaction in queryset_foreign_currency_transactions:
        transaction_date_list.append(transaction.transaction_date.strftime("%Y.%m.%d"))
        my_exchange_rate_list.append(transaction.my_accumulated_rate if transaction.my_accumulated_rate is not None else 0)
        market_exchange_rate_list.append(transaction.market_closing_rate if transaction.my_accumulated_rate is not None else 0)

        if count == 0:
            upper_bound = max(transaction.my_accumulated_rate, transaction.market_closing_rate)
            lower_bound = min(transaction.my_accumulated_rate, transaction.market_closing_rate)
        else:
            if max(transaction.my_accumulated_rate, transaction.market_closing_rate) > upper_bound:
                upper_bound = max(transaction.my_accumulated_rate, transaction.market_closing_rate)
            if min(transaction.my_accumulated_rate, transaction.market_closing_rate) < lower_bound:
                lower_bound = min(transaction.my_accumulated_rate, transaction.market_closing_rate)
        count += 1

    # Add current exchange rate at last
    target_foreign_currency = ForeignCurrency.objects.get(pk=foreign_currency_pk)
    my_rate_mv = target_foreign_currency.accumulated_exchange_rate_mv
    mkt_rate = target_foreign_currency.current_exchange_rate

    transaction_date_list.append(datetime.datetime.today().strftime("%Y.%m.%d"))
    my_exchange_rate_list.append(my_rate_mv)
    market_exchange_rate_list.append(mkt_rate)
    if max(my_rate_mv, mkt_rate) > upper_bound:
        upper_bound = max(my_rate_mv, mkt_rate)
    if min(my_rate_mv, mkt_rate) < lower_bound:
        lower_bound = min(my_rate_mv, mkt_rate)

    color_list = ['#00B0F0', '#FFC000']
    area_color_js = (
        "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
        "[{offset: 0, color: '#eb64fb'}, {offset: 1, color: '#3fbbff0d'}], false)"
    )
    line_graph = (
        Line()
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Exchange History",
                                      title_textstyle_opts=opts.TextStyleOpts(color='#FFFFFF', font_size=25)),
            xaxis_opts=opts.AxisOpts(type_='category',
                                     boundary_gap=False,
                                     axislabel_opts=opts.LabelOpts(margin=20, color="#FFFFFF", rotate=15),
                                     axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color='#FFFFFF')),
                                     axistick_opts=opts.AxisTickOpts(
                                         is_show=True,
                                         length=6,
                                         linestyle_opts=opts.LineStyleOpts(color="#FFFFFF")),
                                     ),
            yaxis_opts=opts.AxisOpts(max_=upper_bound+5,
                                     min_=lower_bound-5,
                                     axislabel_opts=opts.LabelOpts(color='#FFFFFF'),
                                     axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color='#FFFFFF')),
                                     splitline_opts=opts.SplitLineOpts(
                                         is_show=True,
                                         linestyle_opts=opts.LineStyleOpts(color="#FFFFFF1F")
                                     ),
                                     ),
            tooltip_opts=opts.TooltipOpts(background_color='#FFF'),
            legend_opts=opts.LegendOpts(is_show=True,
                                        pos_right='right',
                                        pos_top='center',
                                        textstyle_opts=opts.TextStyleOpts(color='#FFFFFF'),
                                        orient='vertical',
                                        legend_icon=False),
        )
        .set_colors(color_list)
        .add_xaxis(xaxis_data=transaction_date_list)
        .add_yaxis(
            series_name='My Rate',
            y_axis=my_exchange_rate_list,
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=True, position="top", color="white"),
            linestyle_opts=opts.LineStyleOpts(type_='solid', width=3),
        )
        .add_yaxis(
            series_name='MKT Rate',
            y_axis=market_exchange_rate_list,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='solid', width=2.5),
        )
    )

    grid = (
        Grid()
        .add(line_graph,
             grid_opts=opts.GridOpts(
                 pos_top="20%",
                 pos_left="3%",
                 pos_right="10%",
                 pos_bottom="5%",
                 is_contain_label=True,
             ))
        .dump_options_with_quotes()
    )

    return grid


class ForeignCurrencyLineGraphView(APIView):
    def get(self, request, *args, **kwargs):
        foreign_currency_pk = request.__dict__['parser_context']['kwargs']['foreign_currency_pk']
        return json_response(json.loads(foreign_currency_line_graph(request, foreign_currency_pk)))


def foreign_currency_refresh(request):

    my_dashboard = Dashboard.objects.get(owner=request.user)

    queryset_foreign_currencies = ForeignCurrency.objects.filter(dashboard=my_dashboard.pk)
    for foreign_currency in queryset_foreign_currencies:
        foreign_currency.update_statistics()

    return HttpResponseRedirect(reverse('exchangeapp:myexchange_detail', kwargs={'pk': my_dashboard.pk}))


class ForeignCurrencyTransactionCreateView(CreateView):
    model = ForeignCurrencyTransaction
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrencytransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.foreign_currency = ForeignCurrency.objects.get(pk=self.request.POST['foreign_currency_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.amount > temp_transaction.foreign_currency.current_amount:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        # Market Close Rate Insert
        currency_cross_list = [
            temp_transaction.foreign_currency.currency_master.currency_code,
            '/',
            temp_transaction.foreign_currency.dashboard.main_currency.currency_code,
        ]
        currency_cross = ''.join(currency_cross_list)
        target_date = temp_transaction.transaction_date
        one_day = timedelta(days=1)
        market_closing_rate = None
        try:
            market_closing_rate_json = json.loads(ip.get_currency_cross_historical_data(currency_cross,
                                                                                        (target_date - one_day).strftime("%d/%m/%Y"),
                                                                                        target_date.strftime("%d/%m/%Y"),
                                                                                        True))
            market_closing_rate = round(market_closing_rate_json['historical'][0]['close'], 2)
        except Exception as historical_market_data:
            print('Exception for historical_market_data : {}'.format(historical_market_data))
            sleep(5)
            try:
                currency_cross = ''.join(currency_cross_list[::-1])
                market_closing_rate_json = json.loads(ip.get_currency_cross_historical_data(currency_cross,
                                                                                            (target_date - one_day).strftime("%d/%m/%Y"),
                                                                                            target_date.strftime("%d/%m/%Y"),
                                                                                            True))
                market_closing_rate = round(pow(market_closing_rate_json['historical'][0]['close'], -1), 2)
            except Exception as historical_market_data_reverse:
                print('Exception for historical_market_data_reverse : {}'.format(historical_market_data_reverse))

        if market_closing_rate is not None:
            temp_transaction.market_closing_rate = market_closing_rate


        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})


class ForeignCurrencyTransactionDeleteView(DeleteView):
    model = ForeignCurrencyTransaction
    context_object_name = 'target_foreign_currency_transaction'
    template_name = 'exchangeapp/foreigncurrencytransaction_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})


def foreign_currency_transaction_delete_all(request):

    foreign_currency_pk = request.GET['foreign_currency_pk']
    queryset_foreign_currency_transactions = ForeignCurrencyTransaction.objects.filter(foreign_currency=foreign_currency_pk)
    delete_count = 0
    currency = None
    for transaction in queryset_foreign_currency_transactions:
        delete_count += 1
        currency = transaction.foreign_currency.currency_master.currency_code
        transaction.delete()
    print('Delete transaction of {}. {} row(s) deleted.'.format(currency, delete_count))

    target_foreign_currency = ForeignCurrency.objects.get(pk=foreign_currency_pk)
    target_foreign_currency.update_statistics()

    return HttpResponseRedirect(reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': foreign_currency_pk}))