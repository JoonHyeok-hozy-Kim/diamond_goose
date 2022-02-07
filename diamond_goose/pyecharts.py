import json
from random import randrange

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar
from pyecharts import options as opts


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


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