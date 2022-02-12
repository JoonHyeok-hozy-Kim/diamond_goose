import json

from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from pyecharts.charts import Pie
from pyecharts import options as opts
from rest_framework.views import APIView

from dashboardapp.models import Dashboard
from diamond_goose.pyecharts import json_response
from exchangeapp.models import ForeignCurrency
from householdbookapp.forms import LiquidityCreationForm, DebtCreationForm
from householdbookapp.models import Liquidity, Debt
from masterinfoapp.models import CurrencyMaster


class HouseholdbookHomeView(ListView):
    model = Liquidity
    template_name = 'householdbookapp/householdbook_home.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HouseholdbookHomeView, self).get_context_data(**kwargs)

        queryset_my_dashboard = Dashboard.objects.get(owner=self.request.user)
        dashboard_pk = queryset_my_dashboard.pk
        context.update({'dashboard_pk': dashboard_pk})

        # Chart URLs
        ip_address = None
        liquidity_pie_chart_url_list = ['http://']
        debt_pie_chart_url_list = ['http://']
        try:
            from diamond_goose.settings.local import LOCAL_IP_ADDRESS
            ip_address = LOCAL_IP_ADDRESS
        except Exception as deploy_environment:
            print('Householdbook Home Chart - deploy_environment : {}'.format(deploy_environment))
            from diamond_goose.settings.deploy import DEPLOY_IP_ADDRESS
            ip_address = DEPLOY_IP_ADDRESS

        if ip_address:
            liquidity_pie_chart_url_list.append(ip_address)
            liquidity_pie_chart_url_list.append('/householdbook/liquidity_pie_chart/')
            context.update({'liquidity_pie_chart_url_list': ''.join(liquidity_pie_chart_url_list)})

            debt_pie_chart_url_list.append(ip_address)
            debt_pie_chart_url_list.append('/householdbook/debt_pie_chart/')
            context.update({'debt_pie_chart_url_list': ''.join(debt_pie_chart_url_list)})

        return context


class LiquidityListView(ListView):
    model = Liquidity
    template_name = 'householdbookapp/liquidity_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LiquidityListView, self).get_context_data(**kwargs)

        queryset_my_dashboard = Dashboard.objects.get(owner=self.request.user)
        dashboard_pk = queryset_my_dashboard.pk
        context.update({'dashboard_pk': dashboard_pk})

        queryset_my_liquidities = Liquidity.objects.filter(owner=self.request.user,
                                                           dashboard=dashboard_pk)
        total_liquidity_amount = 0

        for liquidity in queryset_my_liquidities:
            liquidity.update_statistics()
            total_liquidity_amount += liquidity.amount_exchanged
        context.update({'queryset_my_liquidities': queryset_my_liquidities})
        context.update({'total_liquidity_amount': total_liquidity_amount})
        context.update({'main_currency_code': queryset_my_dashboard.main_currency.currency_code})

        liquidity_pie_chart_url_list = ['http://']
        ip_address = None
        try:
            from diamond_goose.settings.local import LOCAL_IP_ADDRESS
            ip_address = LOCAL_IP_ADDRESS
        except Exception as deploy_environment:
            print('Liquidity Pie Chart - deploy_environment : {}'.format(deploy_environment))
            from diamond_goose.settings.deploy import DEPLOY_IP_ADDRESS
            ip_address = DEPLOY_IP_ADDRESS

        if ip_address:
            liquidity_pie_chart_url_list.append(ip_address)
            liquidity_pie_chart_url_list.append('/householdbook/liquidity_pie_chart/')
            context.update({'liquidity_pie_chart_url_list': ''.join(liquidity_pie_chart_url_list)})

        return context


class LiquidityCreateView(CreateView):
    model = Liquidity
    form_class = LiquidityCreationForm
    template_name = 'householdbookapp/liquidity_create.html'

    def form_valid(self, form):
        temp_liquidity = form.save(commit=False)
        temp_liquidity.owner = self.request.user
        temp_liquidity.dashboard = Dashboard.objects.get(owner=self.request.user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('householdbookapp:liquidity_list')


class LiquidityUpdateView(UpdateView):
    model = Liquidity
    form_class = LiquidityCreationForm
    template_name = 'householdbookapp/liquidity_update.html'
    context_object_name = 'target_liquidity'

    def get_success_url(self):
        return reverse('householdbookapp:liquidity_list')


class LiquidityDeleteView(DeleteView):
    model = Liquidity
    template_name = 'householdbookapp/liquidity_delete.html'
    context_object_name = 'target_liquidity'

    def get_success_url(self):
        return reverse('householdbookapp:liquidity_list')


def color_list_generator(starting_hex, ending_hex, color_number):
    if color_number == 0:
        result_list = []
    elif color_number == 1:
        result_list = [starting_hex]
    elif color_number == 2:
        result_list = [starting_hex, ending_hex]
    else:
        result_list = ['#' for i in range(color_number)]
        for i in range(3):
            starting = int(starting_hex[2*i+1:2*i+3], 16)
            ending = int(ending_hex[2*i+1:2*i+3], 16)
            delta = (ending-starting)/(color_number-1)
            # print('[in hex] starting : {} / ending : {}'.format(starting_hex[2*i+1:2*i+3], ending_hex[2*i+1:2*i+1+3]))
            # print('[in decimal] starting : {} / ending : {} / delta : {}'.format(starting, ending, delta))
            for j in range(color_number):
                hex_str = str(hex(round(starting+delta*j)))[2:].upper()
                if len(hex_str) < 2:
                    new_hex_str = '0'
                    new_hex_str += hex_str
                    hex_str = new_hex_str
                # print(hex_str)
                result_list[j] += hex_str
    # print(result_list)
    return result_list


def currency_format(amount, currency_master):
    result_text_list = [currency_master.currency_sign, ' ']
    below_period = None
    if currency_master.currency_code != 'KRW':
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


def liquidity_pie_chart(request) -> Pie:
    queryset_liquidity = Liquidity.objects.filter(owner=request.user)
    x_data = []
    y_data = []
    total_amount = 0
    for liquidity in queryset_liquidity:
        x_data.append(liquidity.liquidity_name)
        y_data.append(liquidity.amount_exchanged)
        total_amount += liquidity.amount_exchanged
    data_pair = [list(z) for z in zip(x_data, y_data)]
    data_pair.sort(key=lambda x: x[1])

    # color : #00FACC ~ #002921
    color_list = color_list_generator('#00FACC', '#002921', queryset_liquidity.count())

    # total amount
    queryset_dashboard = Dashboard.objects.get(owner=request.user)
    total_amount_text = ''.join(['Total Amount : ',
                                currency_format(total_amount, queryset_dashboard.main_currency)])

    pie_chart = (
        Pie()
        .add(
            series_name="Liquidity Composition",
            data_pair=data_pair,
            radius=["40%", "70%"],
            # rosetype="radius",
            center=["60%", "60%"],
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .set_colors(
            color_list
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=total_amount_text,
                pos_left="left",
                pos_top="5",
                title_textstyle_opts=opts.TextStyleOpts(color="#FFFFFF", font_size=20),
            ),
            legend_opts=opts.LegendOpts(pos_left="left",
                                        pos_top="center",
                                        orient="vertical",
                                        textstyle_opts=opts.TextStyleOpts(color="#FFFFFF")),
        )
        .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{b}: {c} ({d}%)"
            ),
            label_opts=opts.LabelOpts(color="#FFFFFF"),
        )
        .dump_options_with_quotes()
    )
    return pie_chart


class LiquidityPieChartView(APIView):
    def get(self, request, *args, **kwargs):
        return json_response(json.loads(liquidity_pie_chart(request)))


class DebtListView(ListView):
    model = Debt
    template_name = 'householdbookapp/debt_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DebtListView, self).get_context_data(**kwargs)

        queryset_my_dashboard = Dashboard.objects.get(owner=self.request.user)
        dashboard_pk = queryset_my_dashboard.pk
        context.update({'dashboard_pk': dashboard_pk})

        queryset_my_debts = Debt.objects.filter(owner=self.request.user,
                                                dashboard=dashboard_pk)
        total_debt_amount = 0

        for debt in queryset_my_debts:
            debt.update_statistics()
            if debt.long_term_debt_flag:
                debt.debt_term = 'Long'
            else:
                debt.debt_term = 'Short'
            total_debt_amount += debt.amount_exchanged
        context.update({'queryset_my_debts': queryset_my_debts})
        context.update({'total_debt_amount': total_debt_amount})
        context.update({'main_currency_code': queryset_my_dashboard.main_currency.currency_code})

        debt_pie_chart_url_list = ['http://']
        ip_address = None
        try:
            from diamond_goose.settings.local import LOCAL_IP_ADDRESS
            ip_address = LOCAL_IP_ADDRESS
        except Exception as deploy_environment:
            print('Debt Pie Chart - deploy_environment : {}'.format(deploy_environment))
            from diamond_goose.settings.deploy import DEPLOY_IP_ADDRESS
            ip_address = DEPLOY_IP_ADDRESS

        if ip_address:
            debt_pie_chart_url_list.append(ip_address)
            debt_pie_chart_url_list.append('/householdbook/debt_pie_chart/')
            context.update({'debt_pie_chart_url_list': ''.join(debt_pie_chart_url_list)})

        return context


class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtCreationForm
    template_name = 'householdbookapp/debt_create.html'

    def form_valid(self, form):
        temp_debt = form.save(commit=False)
        temp_debt.owner = self.request.user
        temp_debt.dashboard = Dashboard.objects.get(owner=self.request.user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('householdbookapp:debt_list')


class DebtUpdateView(UpdateView):
    model = Debt
    form_class = DebtCreationForm
    template_name = 'householdbookapp/debt_update.html'
    context_object_name = 'target_debt'

    def get_success_url(self):
        return reverse('householdbookapp:debt_list')


class DebtDeleteView(DeleteView):
    model = Debt
    template_name = 'householdbookapp/debt_delete.html'
    context_object_name = 'target_debt'

    def get_success_url(self):
        return reverse('householdbookapp:debt_list')


def debt_pie_chart(request) -> Pie:
    queryset_debt = Debt.objects.filter(owner=request.user)
    x_data = []
    y_data = []
    total_amount = 0
    for debt in queryset_debt:
        x_data.append(debt.debt_name)
        y_data.append(debt.amount_exchanged)
        total_amount += debt.amount_exchanged
    data_pair = [list(z) for z in zip(x_data, y_data)]
    data_pair.sort(key=lambda x: x[1])

    # color : #F7A03B ~ #6B451A
    color_list = color_list_generator('#F7A03B', '#6B451A', queryset_debt.count())

    # total amount
    queryset_dashboard = Dashboard.objects.get(owner=request.user)
    total_amount_text = ''.join(['Total Amount : ',
                                currency_format(total_amount, queryset_dashboard.main_currency)])

    pie_chart = (
        Pie()
        .add(
            series_name="Liquidity Composition",
            data_pair=data_pair,
            radius=["40%", "70%"],
            # rosetype="radius",
            center=["60%", "60%"],
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .set_colors(
            color_list
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=total_amount_text,
                pos_left="left",
                pos_top="5",
                title_textstyle_opts=opts.TextStyleOpts(color="#FFFFFF", font_size=20),
            ),
            legend_opts=opts.LegendOpts(pos_left="left",
                                        pos_top="center",
                                        orient="vertical",
                                        textstyle_opts=opts.TextStyleOpts(color="#FFFFFF")),
        )
        .set_series_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="item", formatter="{b}: {c} ({d}%)"
            ),
            label_opts=opts.LabelOpts(color="#FFFFFF"),
        )
        .dump_options_with_quotes()
    )
    return pie_chart


class DebtPieChartView(APIView):
    def get(self, request, *args, **kwargs):
        return json_response(json.loads(debt_pie_chart(request)))

