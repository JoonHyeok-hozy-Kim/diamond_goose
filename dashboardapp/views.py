import json
from datetime import datetime

from django import utils
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import FormMixin
from pyecharts.charts import Pie, Grid
from pyecharts import options as opts
from rest_framework.views import APIView

from assetapp.models import Asset
from dashboardapp.decorators import dashboard_ownership_required
from dashboardapp.forms import DashboardCreationForm
from dashboardapp.models import Dashboard
from diamond_goose.pyecharts import json_response
from householdbookapp.models import Liquidity, Debt
from portfolioapp.forms import PortfolioCreationForm
from portfolioapp.models import Portfolio

has_ownership = [login_required, dashboard_ownership_required]


class DashboardCreateView(CreateView):
    model = Dashboard
    form_class = DashboardCreationForm
    context_object_name = 'target_dashboard'
    template_name = 'dashboardapp/create.html'

    def form_valid(self, form):
        target_dashboard = form.save(commit=False)
        target_dashboard.owner = self.request.user
        target_dashboard.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboardapp:detail', kwargs={'pk':self.object.pk})


@method_decorator(has_ownership, 'get')
class DashboardDetailView(DetailView, FormMixin):
    model = Dashboard
    context_object_name = 'target_dashboard'
    form_class = PortfolioCreationForm
    template_name = 'dashboardapp/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardDetailView, self).get_context_data(**kwargs)

        initial_date = self.object.initial_date.replace(tzinfo=None)
        today = datetime.today()
        time_diff = today-initial_date
        d_day_count = time_diff.days
        context.update({'d_day_count': d_day_count})

        total_liquidity_amount = 0
        total_asset_amount = 0
        try:
            queryset_my_portfolio = Portfolio.objects.get(owner=self.request.user,
                                                          dashboard=self.object.pk)
            context.update({'target_portfolio_pk': queryset_my_portfolio.pk})

            queryset_my_liquidities = Liquidity.objects.filter(dashboard=self.object.pk)

            for liquidity in queryset_my_liquidities:
                total_liquidity_amount += liquidity.amount_exchanged
            total_asset_amount += queryset_my_portfolio.current_value + total_liquidity_amount

        except Exception as identifier:
            print('Dashboard Detail my_portfolio query :', identifier)

        queryset_my_debts = Debt.objects.filter(dashboard=self.object.pk)
        long_term_debt_amount = 0
        short_term_debt_amount = 0
        for debt in queryset_my_debts:
            if debt.long_term_debt_flag:
                long_term_debt_amount += debt.amount_exchanged
            else:
                short_term_debt_amount += debt.amount_exchanged
        total_debt_amount = long_term_debt_amount + short_term_debt_amount
        net_capital_amount = total_asset_amount - total_debt_amount

        context.update({
            'date_today': datetime.today().strftime('%Y.%m.%d'),
            'total_asset_amount': self.set_format_mask(total_asset_amount),
            'net_capital_amount': self.set_format_mask(net_capital_amount),
            'total_debt_amount': self.set_format_mask(total_debt_amount),
        })


        asset_summary_pie_chart_url_list = ['http://']
        ip_address = None
        try:
            from diamond_goose.settings.local import LOCAL_IP_ADDRESS
            ip_address = LOCAL_IP_ADDRESS
        except Exception as deploy_environment:
            print('Liquidity Pie Chart - deploy_environment : {}'.format(deploy_environment))
            from diamond_goose.settings.deploy import DEPLOY_IP_ADDRESS
            ip_address = DEPLOY_IP_ADDRESS

        if ip_address:
            asset_summary_pie_chart_url_list.append(ip_address)
            asset_summary_pie_chart_url_list.append('/dashboard/detail_asset_summary_pie_chart/')
            context.update({'asset_summary_pie_chart_url_list': ''.join(asset_summary_pie_chart_url_list)})

        return context

    def set_format_mask(self, amount):
        main_currency = self.object.main_currency
        result_text_list = [main_currency.currency_sign, ' ']
        below_period = None
        if main_currency.currency_code != 'KRW':
            below_period = str(round(amount, 2)).split('.')[-1]

        integer_list = []
        while amount >= 1000:
            temp_num_str = str(round(amount%1000))
            while len(temp_num_str) < 3:
                temp_num_str = '0' + temp_num_str
            integer_list.append(temp_num_str)
            amount /= 1000
        integer_list.append(str(round(amount)))

        for i in range(len(integer_list)):
            result_text_list.append(integer_list[(i+1)*(-1)])
            result_text_list.append(',')
        result_text_list.pop(-1)
        if below_period:
            result_text_list.append('.')
            result_text_list.append(below_period)
        return ''.join(result_text_list)


def asset_summary_pie_chart_data_generator(request, dashboard_pk):
    large_x_data = []
    large_y_data = []
    large_color_list = []
    total_asset_amount = 0

    queryset_liquidity = Liquidity.objects.filter(dashboard=dashboard_pk)
    for liquidity in queryset_liquidity:
        large_x_data.append(liquidity.liquidity_name)
        large_y_data.append(liquidity.amount_exchanged)
        large_color_list.append("#068CD6")
        total_asset_amount += liquidity.amount_exchanged

    queryset_portfolio = Portfolio.objects.get(dashboard=dashboard_pk)
    queryset_my_assets = Asset.objects.filter(portfolio=queryset_portfolio.pk,
                                              position_opened_flag=True)
    for asset in queryset_my_assets:
        large_x_data.append(asset.asset_master.name)
        large_y_data.append(asset.total_amount_exchanged)
        large_color_list.append(asset.asset_master.asset_type_master.color_hex)
        total_asset_amount += asset.total_amount_exchanged
    large_data_pair = [list(z) for z in zip(large_x_data, large_y_data)]

    small_x_data = ['Total Asset']
    small_y_data = [total_asset_amount]
    small_color_list = ["#264257"]
    queryset_my_debts = Debt.objects.filter(dashboard=dashboard_pk)
    for debt in queryset_my_debts:
        small_x_data.append(debt.debt_name)
        small_y_data.append(debt.amount_exchanged)
        if debt.long_term_debt_flag:
            small_color_list.append("#300600")
        else:
            small_color_list.append("#5C0B00")
    small_data_pair = [list(z) for z in zip(small_x_data, small_y_data)]
    small_data_pair.reverse()
    small_color_list.reverse()
    large_color_list += small_color_list

    return {
        'large_data_pair': large_data_pair,
        'large_color_list': large_color_list,
        'small_data_pair': small_data_pair,
        'small_color_list': small_color_list,
    }


def asset_summary_pie_chart(request, dump_option=False) -> Pie:
    queryset_my_dashboard = Dashboard.objects.get(owner=request.user)
    chart_base_data = asset_summary_pie_chart_data_generator(request, queryset_my_dashboard.pk)
    large_data_pair, large_color_list = chart_base_data['large_data_pair'], chart_base_data['large_color_list']
    large_pie_chart = Pie()
    large_pie_chart.add(
            series_name="Asset Composition",
            data_pair=large_data_pair,
            radius=["40%", "70%"],
            label_opts=opts.LabelOpts(is_show=True, position="center"),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#081321", border_width=1)
        )
    large_pie_chart.set_colors(
            large_color_list
        )
    large_pie_chart.set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{b}: {c} ({d}%)"
            ),
            label_opts=opts.LabelOpts(color="#FFFFFF"),
        )
    large_pie_chart.set_global_opts(legend_opts=opts.LegendOpts(is_show=False))


    small_data_pair, small_color_list = chart_base_data['small_data_pair'], chart_base_data['small_color_list']
    small_pie_chart = Pie()
    small_pie_chart.add(
            series_name="Leverage Status",
            data_pair=small_data_pair,
            radius=["30%", "40%"],
            label_opts=opts.LabelOpts(is_show=False,),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#081321", border_width=1),
        )
    small_pie_chart.set_colors(
        small_color_list
    )
    small_pie_chart.set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{b}: {c} ({d}%)"
            ),
            label_opts=opts.LabelOpts(color="#FFFFFF"),
        )
    small_pie_chart.set_global_opts(legend_opts=opts.LegendOpts(is_show=False))

    grid = Grid()
    grid.add(
        chart=large_pie_chart,
        grid_opts=opts.GridOpts(pos_top="60%",
                                pos_right="10%")
    )
    grid.add(
        chart=small_pie_chart,
        grid_opts=opts.GridOpts(pos_top="60%",
                                pos_right="10%")
    )
    dump_grid = grid.dump_options_with_quotes()

    if dump_option:
        return dump_grid
    else:
        return grid


class AssetSummaryPieChartView(APIView):
    def get(self, request, *args, **kwargs):
        return json_response(json.loads(asset_summary_pie_chart(self.request, dump_option=True)))