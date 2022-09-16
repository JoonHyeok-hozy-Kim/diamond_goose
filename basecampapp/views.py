import json
import datetime
from random import randint
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from assetapp.models import Asset
from diamond_goose.pyecharts import json_response
from masterinfoapp.models import AssetMaster, CurrencyMaster


def about_this_view(request):
    return render(request, 'basecampapp/about_this.html')
    # return render(request, 'accountapp/temp_welcome.html')

def diamond_goose_home_view(request):
    total_asset_amount = float(randint(80000000, 100000000)) + .64
    capital_rate = randint(90, 95) / 100

    dollar_object = CurrencyMaster.objects.get(currency_code='USD')
    from diamond_goose.factory import format_mask_currency
    context = {
        'date_today': datetime.datetime.today().strftime('%Y.%m.%d'),
        'd_day_count': randint(200, 400),
        'total_asset_amount': format_mask_currency(total_asset_amount, dollar_object),
        'net_capital_amount': format_mask_currency(total_asset_amount*capital_rate, dollar_object),
        'total_debt_amount': format_mask_currency(total_asset_amount*(1-capital_rate), dollar_object),
    }

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
        asset_summary_pie_chart_url_list.append('/basecamp/pie_chart_clone/')
        # context.update({'asset_summary_pie_chart_url_list': ''.join(asset_summary_pie_chart_url_list)})
        context['asset_summary_pie_chart_url_list'] = ''.join(asset_summary_pie_chart_url_list)

    print('------------------------------HOZY DEBUG------------------------------')
    # fake_asset_summary_pie_chart_data_generator()
    print('------------------------------HOZY DEBUG------------------------------')
    return render(context=context, request=request, template_name='basecampapp/diamond_goose_home.html')


def fake_asset_summary_pie_chart_data_generator():
    large_x_data = []
    large_y_data = []
    large_color_list = []
    total_asset_amount = 0
    large_pie_element_count = 0


    # Fake Liquidity Data
    liquidity_amount_lower_bound = 20000
    liquidity_amount_upper_bound = 60000
    fake_liquidity_list = [
        ['KRW Cash', randint(liquidity_amount_lower_bound, liquidity_amount_upper_bound)],
        ['USD Cash', randint(liquidity_amount_lower_bound, liquidity_amount_upper_bound)],
        ['Bank Deposit', randint(liquidity_amount_lower_bound, liquidity_amount_upper_bound)],
    ]

    for liquidity in fake_liquidity_list:
        large_x_data.append(liquidity[0])
        large_y_data.append(liquidity[1])
        large_color_list.append("#068CD6")
        total_asset_amount += liquidity[1]
        large_pie_element_count += 1


    # Random Asset Data
    random_queryset_asset_master = AssetMaster.objects.get_queryset().order_by('asset_type_master__asset_type_code')

    for asset_master in random_queryset_asset_master:
        random_select = randint(0, 1)
        if random_select == 0 and asset_master.asset_type_master is not None:
            random_amount = randint(10000, 30000)
            large_x_data.append(asset_master.name)
            large_y_data.append(random_amount)
            large_color_list.append(asset_master.asset_type_master.color_hex)
            total_asset_amount += random_amount
            large_pie_element_count += 1


    small_x_data = []
    small_y_data = []
    small_color_list = []
    total_debt_amount = 0

    # dummy data append due to large_colors
    for i in range(large_pie_element_count):
        small_x_data.append('')
        small_y_data.append(0)

    # Fake Debt data creation
    fake_debt_list = [
        ['Credit Card', randint(10000, 30000)],
        ['Student Loan', randint(10000, 30000)],
        ['Mortgage', randint(10000, 30000)],
    ]
    for debt in fake_debt_list:
        small_x_data.append(debt[0])
        large_x_data.append('')
        small_y_data.append(debt[1])
        large_y_data.append(0)
        large_color_list.append("#FA0067")
        total_debt_amount += debt[1]

    # Actual Net Capital data creation
    small_x_data.append('Net Capital')
    large_x_data.append('')
    small_y_data.append(total_asset_amount-total_debt_amount)
    large_y_data.append(0)
    large_color_list.append("#17344A")



    large_data_pair = [list(z) for z in zip(large_x_data, large_y_data)]
    small_data_pair = [list(z) for z in zip(small_x_data, small_y_data)]

    leverage_rate = 0
    if total_asset_amount > 0:
        leverage_rate = total_debt_amount/total_asset_amount


    # print(large_data_pair)
    # print(large_color_list)
    # print(small_data_pair)
    # print(small_color_list)
    # print(str(round(leverage_rate * 100, 2)) + '%')

    return {
        'large_data_pair': large_data_pair,
        'large_color_list': large_color_list,
        'small_data_pair': small_data_pair,
        'small_color_list': small_color_list,
        'leverage_rate': str(round(leverage_rate*100, 2))+'%',
    }

class SimulationAssetSummaryPieChartView(APIView):
    def get(self, request, *args, **kwargs):
        from dashboardapp.views import asset_summary_pie_chart
        print('----> HOZY DEBUG in SimulationAssetSummaryPieChartView')
        return json_response(json.loads(asset_summary_pie_chart(self.request, dump_option=True, simulation_flag=True)))


def fake_asset_history_line_graph_data_generator():

    x_data = []
    line_y_data = [
        {'name': 'Asset', 'data_set': []},
        {'name': 'Liquidity', 'data_set': []},
        {'name': 'Investment', 'data_set': []},
        {'name': 'Net Capital', 'data_set': []},
        {'name': 'Dept', 'data_set': []},
    ]

    number_of_dates_recorded = randint(80, 90)
    final_date = datetime.datetime.today()
    initial_date = final_date - datetime.timedelta(days=number_of_dates_recorded)

    final_total_asset_amount = float(randint(80000000, 100000000)) + .64
    max_y_value = final_total_asset_amount
    var_total_asset_amount = final_total_asset_amount / 10
    asset_amount_delta = (final_total_asset_amount - var_total_asset_amount) / number_of_dates_recorded

    for date_num in range(number_of_dates_recorded):
        current_date = initial_date + datetime.timedelta(days=date_num)
        x_data.append(current_date.strftime('%Y.%m.%d'))

        var_total_asset_amount += asset_amount_delta
        temp_total_asset_amount = var_total_asset_amount * randint(90, 110) / 100
        temp_liquidity_amount = temp_total_asset_amount * randint(10, 20) / 100
        temp_debt_amout = final_total_asset_amount * randint(5, 10) / 100

        for statistic in line_y_data:
            if statistic['name'] =='Asset'           :     statistic['data_set'].append(temp_total_asset_amount)
            if statistic['name'] =='Liquidity'       :     statistic['data_set'].append(temp_liquidity_amount)
            if statistic['name'] =='Investment'      :     statistic['data_set'].append(temp_total_asset_amount - temp_liquidity_amount)
            if statistic['name'] =='Net Capital'     :     statistic['data_set'].append(temp_total_asset_amount - temp_debt_amout)
            if statistic['name'] =='Dept'            :     statistic['data_set'].append(temp_debt_amout)

    return {
        'x_data': x_data,
        'line_y_data': line_y_data,
        'max_y_value': round(max_y_value * 1.1),
    }