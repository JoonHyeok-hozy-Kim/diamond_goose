from django.contrib.auth.models import User
from django.http import HttpResponseForbidden


def account_ownership_required(func):
    def decorated(request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if request.user != user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated


def profile_ownership_required(func):
    def decorated(request, *args, **kwargs):
        from accountapp.models import Profile
        profile = Profile.objects.get(pk=kwargs['pk'])
        if request.user != profile.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated
