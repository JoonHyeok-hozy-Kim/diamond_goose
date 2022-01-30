from django.forms import ModelForm

from portfolioapp.models import Portfolio


class PortfolioCreationForm(ModelForm):
    class Meta:
        model = Portfolio
        fields = []

