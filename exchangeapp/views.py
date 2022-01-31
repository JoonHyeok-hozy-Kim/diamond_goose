from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import DetailView, CreateView, ListView
from django.views.generic.edit import FormMixin, DeleteView

from dashboardapp.models import Dashboard
from exchangeapp.forms import ForeignCurrencyCreationForm, ForeignCurrencyTransactionCreationForm
from exchangeapp.models import ForeignCurrency, ForeignCurrencyTransaction
from masterinfoapp.models import CurrencyMaster


class MyExchangeDetailView(DetailView):
    model = Dashboard
    context_object_name = 'my_dashboard'
    template_name = 'exchangeapp/myexchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MyExchangeDetailView, self).get_context_data(**kwargs)

        queryset_foreign_currencies = ForeignCurrency.objects.filter(owner=self.request.user,
                                                                    dashboard=self.object.pk)
        context.update({'queryset_foreign_currencies': queryset_foreign_currencies})
        context.update({'myexchange_detail_flag': True})

        return context


class MyExchangeCurrencyMasterListView(ListView):
    model = CurrencyMaster
    template_name = 'masterinfoapp/currencymaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyExchangeCurrencyMasterListView, self).get_context_data(**kwargs)

        query_currency_master_list = CurrencyMaster.objects.exclude(id__in=Dashboard.objects.filter(owner=self.request.user).values('main_currency_id')).exclude(id__in=ForeignCurrency.objects.filter(owner=self.request.user).values('currency_master_id')).order_by('currency_code')
        for currency_master in query_currency_master_list:
            currency_master.name = Truncator(currency_master.currency_name).chars(29)
        context.update({'query_currency_master_list': query_currency_master_list})
        context.update({'myexchange_currencymaster_list_flag': True})

        return context


class MyExchangeCurrencyMasterDetailView(DetailView, FormMixin):
    model = CurrencyMaster
    form_class = ForeignCurrencyCreationForm
    context_object_name = 'target_currency_master'
    template_name = 'template_currencymaster_detail.html'

    def get_context_data(self, **kwargs):

        context = super(MyExchangeCurrencyMasterDetailView, self).get_context_data(**kwargs)
        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'myexchange_currency_master_flag': True})

        return context


class ForeignCurrencyCreateView(CreateView):
    model = ForeignCurrency
    form_class = ForeignCurrencyCreationForm
    template_name = 'exchangeapp/foreigncurrency_create.html'

    def form_valid(self, form):
        temp_currency = form.save(commit=False)
        currency_master_pk = self.request.POST['currency_master_pk']

        temp_currency.dashboard = Dashboard.objects.get(owner=self.request.user)
        temp_currency.owner = self.request.user
        temp_currency.currency_master = CurrencyMaster.objects.get(pk=currency_master_pk)
        temp_currency.save()

        return super().form_valid(form)

    def get_success_url(self):
        target_dashboard = Dashboard.objects.get(owner=self.request.user)
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': target_dashboard.pk})


class ForeignCurrencyDeleteView(DeleteView):
    model = ForeignCurrency
    context_object_name = 'target_foreign_currency'
    template_name = 'exchangeapp/foreigncurrency_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': self.object.dashboard.pk})


class ForeignCurrencyDetailView(DetailView, FormMixin):
    model = ForeignCurrency
    context_object_name = 'target_foreign_currency'
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrency_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ForeignCurrencyDetailView, self).get_context_data(**kwargs)

        queryset_transaction_list = ForeignCurrencyTransaction.objects.filter(foreign_currency=self.object.pk).order_by("-transaction_date")
        context.update({'queryset_transaction_list': queryset_transaction_list})

        # Update Foreign Currency Stats.
        self.object.update_statistics()

        return context


# def foreign_currency_refresh(request):
#
#     foreign_currency_pk = request.GET['foreign_currency_pk']
#
#     target_foreign_currency = ForeignCurrency.objects.get(pk=foreign_currency_pk)
#
#     target_foreign_currency.update_current_rate()
#     target_foreign_currency.refresh_from_db()
#     target_foreign_currency.update_quantity_amount_rates()
#     target_foreign_currency.refresh_from_db()
#
#     return HttpResponseRedirect(reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': foreign_currency_pk}))


class ForeignCurrencyTransactionCreateView(CreateView):
    model = ForeignCurrencyTransaction
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrencytransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.foreign_currency = ForeignCurrency.objects.get(pk=self.request.POST['foreign_currency_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.amount > temp_transaction.foreign_currency.current_amount:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})


class ForeignCurrencyTransactionDeleteView(DeleteView):
    model = ForeignCurrencyTransaction
    context_object_name = 'target_foreign_currency_transaction'
    template_name = 'exchangeapp/foreigncurrencytransaction_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})


def foreign_currency_transaction_delete_all(request):

    foreign_currency_pk = request.GET['foreign_currency_pk']
    queryset_foreign_currency_transactions = ForeignCurrencyTransaction.objects.filter(foreign_currency=foreign_currency_pk)
    delete_count = 0
    currency = None
    for transaction in queryset_foreign_currency_transactions:
        delete_count += 1
        currency = transaction.foreign_currency.currency_master.currency_code
        transaction.delete()
    print('Delete transaction of {}. {} row(s) deleted.'.format(currency, delete_count))

    target_foreign_currency = ForeignCurrency.objects.get(pk=foreign_currency_pk)
    target_foreign_currency.update_statistics()

    return HttpResponseRedirect(reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': foreign_currency_pk}))