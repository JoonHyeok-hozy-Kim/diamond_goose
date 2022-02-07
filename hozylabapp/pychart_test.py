# from jinja2 import Environment, FileSystemLoader
# from pyecharts.globals import CurrentConfig
# from django.http import HttpResponse
#
# CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates/pyecharts"))
#
# from pyecharts import options as opts
# from pyecharts.charts import Bar
#
#
# def index(request):
#     c = (
#         Bar()
#         .add_xaxis(["x축1", "x축2", "x축3", "x축4", "x축5", "x축6"])
#         .add_yaxis("빨갱이", [5, 20, 36, 10, 75, 90])
#         .add_yaxis("파랭이", [15, 25, 16, 55, 48, 8])
#         .set_global_opts(title_opts=opts.TitleOpts(title="전체 제목", subtitle="소제목"))
#     )
#     return HttpResponse(c.render_embed())

import json
from random import randrange

from django.http import HttpResponse
from django.views.generic import ListView
from rest_framework.views import APIView

from pyecharts.charts import Bar
from pyecharts import options as opts

from diamond_goose.pyecharts import json_error, json_response, response_as_json


# Create your views here.
from portfolioapp.models import Portfolio

class PyechartTestHomeView(ListView):
    model = Portfolio
    template_name = 'hozylabapp/pyechart_test_000.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PyechartTestHomeView, self).get_context_data(**kwargs)

        return context

def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["x1", "x2", "x3", "x4", "x5", "x6"])
        .add_yaxis("A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar Graph", subtitle="부제목"))
        .dump_options_with_quotes()
    )
    return c


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return json_response(json.loads(bar_base()))