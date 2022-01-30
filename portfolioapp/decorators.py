from django.http import HttpResponseForbidden

from portfolioapp.models import Portfolio


def portfolio_ownership_required(func):
    def decorated(request, *args, **kwargs):
        portfolio = Portfolio.objects.get(pk=kwargs['pk'])
        if request.user != portfolio.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated