from django.forms import ModelForm, widgets

from dashboardapp.models import Dashboard


class DashboardCreationForm(ModelForm):
    class Meta:
        model = Dashboard
        fields = [
            'main_currency',
            'initial_date',
        ]

        widgets = {
            'initial_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }