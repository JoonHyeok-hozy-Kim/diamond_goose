from django.http import HttpResponseForbidden

from assetapp.models import Asset


def asset_ownership_required(func):
    def decorated(request, *args, **kwargs):
        equity = Asset.objects.get(pk=kwargs['pk'])
        if request.user != equity.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated