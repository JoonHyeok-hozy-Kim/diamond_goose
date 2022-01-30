from django.http import HttpResponseForbidden

from pensionapp.models import Pension


def pension_ownership_required(func):
    def decorated(request, *args, **kwargs):
        pension = Pension.objects.get(pk=kwargs['pk'])
        if request.user != pension.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated


# def pension_asset_ownership_required(func):
#     def decorated(request, *args, **kwargs):
#         pension_asset = PensionAsset.objects.get(pk=kwargs['pk'])
#         if request.user != pension_asset.owner:
#             return HttpResponseForbidden()
#         return func(request, *args, **kwargs)
#
#     return decorated