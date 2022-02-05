from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.text import Truncator
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from masterinfoapp.forms import AssetMasterCreationForm, CurrencyMasterCreationForm, PensionMasterCreationForm
from masterinfoapp.models import AssetMaster, CurrencyMaster, PensionMaster


class AssetMasterCreateView(CreateView):
    model = AssetMaster
    form_class = AssetMasterCreationForm
    template_name = 'masterinfoapp/assetmaster_create.html'

    def get_success_url(self):
        return reverse('masterinfoapp:assetmaster_list')


class AssetMasterListView(ListView):
    model = AssetMaster
    template_name = 'masterinfoapp/assetmaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetMasterListView, self).get_context_data(**kwargs)

        query_asset_master_list = AssetMaster.objects.all().order_by('asset_type', 'ticker')
        for asset_master in query_asset_master_list:
            asset_master.name = Truncator(asset_master.name).chars(29)
        context.update({'query_asset_master_list': query_asset_master_list})
        context.update({'asset_master_list_view_flag': True})

        return context


class AssetMasterDetailView(DetailView):
    model = AssetMaster
    context_object_name = 'target_asset_master'
    template_name = 'template_assetmaster_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.update_current_price()
        self.object.refresh_from_db()

        context = super(AssetMasterDetailView, self).get_context_data(**kwargs)

        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'assetmaster_detail_view_flag': True})

        return context


class AssetMasterUpdateView(UpdateView):
    model = AssetMaster
    form_class = AssetMasterCreationForm
    context_object_name = 'target_asset_master'
    template_name = 'masterinfoapp/assetmaster_update.html'

    def get_success_url(self):
        return reverse('masterinfoapp:assetmaster_detail', kwargs={'pk':self.object.pk})


class AssetMasterDeleteView(DeleteView):
    model = AssetMaster
    context_object_name = 'target_asset_master'
    template_name = 'masterinfoapp/assetmaster_delete.html'

    def get_success_url(self):
        return reverse('masterinfoapp:assetmaster_list')


class CurrencyMasterCreateView(CreateView):
    model = CurrencyMaster
    form_class = CurrencyMasterCreationForm
    template_name = 'masterinfoapp/currencymaster_create.html'

    def get_success_url(self):
        return reverse('masterinfoapp:currencymaster_list')


class CurrencyMasterListView(ListView):
    model = CurrencyMaster
    template_name = 'masterinfoapp/currencymaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CurrencyMasterListView, self).get_context_data(**kwargs)

        query_currency_master_list = CurrencyMaster.objects.all().order_by('currency_code')
        for currency_master in query_currency_master_list:
            currency_master.name = Truncator(currency_master.currency_name).chars(29)
        context.update({'query_currency_master_list': query_currency_master_list})
        context.update({'masterinfoapp_currency_master_list_flag': True})
        return context


class CurrencyMasterDetailView(DetailView):
    model = CurrencyMaster
    context_object_name = 'target_currency_master'
    template_name = 'template_currencymaster_detail.html'

    def get_context_data(self, **kwargs):

        context = super(CurrencyMasterDetailView, self).get_context_data(**kwargs)

        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'masterinfoapp_currency_master_flag': True})

        return context


class CurrencyMasterDeleteView(DeleteView):
    model = CurrencyMaster
    context_object_name = 'target_currency_master'
    template_name = 'masterinfoapp/currencymaster_delete.html'

    def get_success_url(self):
        return reverse('masterinfoapp:currencymaster_list')


class CurrencyMasterUpdateView(UpdateView):
    model = CurrencyMaster
    form_class = CurrencyMasterCreationForm
    context_object_name = 'target_currency_master'
    template_name = 'masterinfoapp/currencymaster_update.html'

    def get_success_url(self):
        return reverse('masterinfoapp:currencymaster_list')


class PensionMasterCreateView(CreateView):
    model = PensionMaster
    form_class = PensionMasterCreationForm
    template_name = 'masterinfoapp/pensionmaster_create.html'

    def get_success_url(self):
        return reverse('masterinfoapp:pensionmaster_list')


class PensionMasterListView(ListView):
    model = PensionMaster
    template_name = 'masterinfoapp/pensionmaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionMasterListView, self).get_context_data(**kwargs)

        query_pension_master_list = PensionMaster.objects.all().order_by('pension_name')
        for pension_master in query_pension_master_list:
            pension_master.name = Truncator(pension_master.pension_name).chars(29)
        context.update({'query_pension_master_list': query_pension_master_list})
        return context


class PensionMasterUpdateView(UpdateView):
    model = PensionMaster
    form_class = PensionMasterCreationForm
    context_object_name = 'target_pension_master'
    template_name = 'masterinfoapp/pensionmaster_update.html'

    def get_success_url(self):
        return reverse('masterinfoapp:pensionmaster_list')