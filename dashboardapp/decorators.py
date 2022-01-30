from django.http import HttpResponseForbidden

from dashboardapp.models import Dashboard


def dashboard_ownership_required(func):
    def decorated(request, *args, **kwargs):
        dashboard = Dashboard.objects.get(pk=kwargs['pk'])
        if request.user != dashboard.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated