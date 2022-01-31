import json

from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils.text import Truncator
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin, DeleteView

from assetapp.models import PensionAsset, AssetTransaction
from assetapp.views import AssetTransactionDeleteView
from dashboardapp.models import Dashboard
from masterinfoapp.models import AssetMaster
from pensionapp.forms import PensionCreationForm, PensionTransactionCreationForm, PensionAssetCreationForm, \
    PensionAssetTransactionCreationForm
from pensionapp.models import Pension, PensionTransaction
from portfolioapp.models import Portfolio


class PensionCreateView(CreateView):
    model = Pension
    form_class = PensionCreationForm
    template_name = 'pensionapp/pension_create.html'

    def form_valid(self, form):
        temp_pension = form.save(commit=False)
        temp_pension.owner = self.request.user
        temp_pension.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_pension.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pensionapp:pension_list')


class PensionListView(ListView):
    model = Pension
    context_object_name = 'pension_list'
    template_name = 'pensionapp/pension_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionListView, self).get_context_data(**kwargs)

        queryset_my_portfolio = Portfolio.objects.get(owner=self.request.user)
        my_portfolio_pk = queryset_my_portfolio.pk
        context.update({'my_portfolio_pk': my_portfolio_pk})

        return context


class PensionDetailView(DetailView, FormMixin):
    model = Pension
    form_class = PensionTransactionCreationForm
    context_object_name = 'target_pension'
    template_name = 'pensionapp/pension_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionDetailView, self).get_context_data(**kwargs)

        # Update Pension Stats
        self.object.update_statistics()
        self.object.refresh_from_db()

        context.update({'my_pension_pk': self.object.pk})

        pension_asset_list = PensionAsset.objects.filter(pension=self.object.pk)
        context.update({'pension_asset_list': pension_asset_list})

        not_pension_asset_list = PensionAsset.objects.filter()
        context.update({'not_pension_asset_list': not_pension_asset_list})

        return context


class PensionTransactionCreateView(CreateView):
    model = PensionTransaction
    form_class = PensionTransactionCreationForm
    template_name = 'pensionapp/pensiontransaction_create.html'

    def form_valid(self, form):
        temp_pension_transaction = form.save(commit=False)
        temp_pension_transaction.owner = self.request.user
        temp_pension_transaction.pension = Pension.objects.get(pk=self.request.POST['pension_pk'])
        temp_pension_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pensionapp:pension_detail', kwargs={'pk': self.request.POST['pension_pk']})


class PensionTransactionDetailView(DetailView, FormMixin):
    model = PensionTransaction
    form_class = PensionTransactionCreationForm
    template_name = 'pensionapp/pensiontransaction_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionTransactionDetailView, self).get_context_data(**kwargs)

        # Update Pension Stats
        self.object.pension.calculate_total_paid_amount()
        self.object.pension.refresh_from_db()

        return context


class PensionTransactionDeleteView(DeleteView):
    model = PensionTransaction
    context_object_name = 'target_pension_transaction'
    template_name = 'pensionapp/pensiontransaction_delete.html'

    def get_success_url(self):
        return reverse('pensionapp:pension_detail', kwargs={'pk': self.request.POST['pension_pk']})


class PensionAssetMasterNotMineListView(ListView):
    model = AssetMaster
    template_name = 'masterinfoapp/assetmaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionAssetMasterNotMineListView, self).get_context_data(**kwargs)

        request_dict = self.request.__dict__
        pension_pk = request_dict['path'].split('/')[-1]

        query_asset_master_list = AssetMaster.objects.filter(asset_type='PENSION_ASSET').exclude(id__in=PensionAsset.objects.filter(pension=pension_pk).values('asset_master_id')).order_by('ticker')
        for asset_master in query_asset_master_list:
            asset_master.name = Truncator(asset_master.name).chars(29)
        context.update({'query_asset_master_list': query_asset_master_list})
        context.update({'pensionasset_assetmaster_list_flag': True})
        context.update({'pension_pk': pension_pk})

        return context


class PensionAssetMasterNotMineDetailView(DetailView):
    model = AssetMaster
    context_object_name = 'target_asset_master'
    template_name = 'pensionapp/pensionasset_assetmaster_notmine_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.update_current_price()
        self.object.refresh_from_db()

        context = super(PensionAssetMasterNotMineDetailView, self).get_context_data(**kwargs)

        request_dict = self.request.__dict__
        pension_pk = request_dict['path'].split('/')[-2]
        target_pension = Pension.objects.get(pk=pension_pk)
        asset_pk = request_dict['path'].split('/')[-1]

        context.update({'target_pension': target_pension})
        context.update({'asset_pk': asset_pk})
        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'pensionasset_assetmaster_notmine_detail_flag': True})

        return context


class PensionAssetCreateView(CreateView):
    model = PensionAsset
    template_name = 'pensionapp/pensionasset_create.html'
    form_class = PensionAssetCreationForm

    def form_valid(self, form):
        temp_pension_asset = form.save(commit=False)

        asset_pk = self.request.POST['asset_pk']
        pension_pk = self.request.POST['pension_pk']
        target_pension = Pension.objects.get(pk=pension_pk)
        portfolio_pk = target_pension.portfolio.pk

        temp_pension_asset.owner = self.request.user
        temp_pension_asset.asset_master = AssetMaster.objects.get(pk=asset_pk)
        temp_pension_asset.portfolio = Portfolio.objects.get(pk=portfolio_pk)
        temp_pension_asset.pension = target_pension
        temp_pension_asset.save()

        return super().form_valid(form)

    def get_success_url(self):
        pension_pk = self.request.POST['pension_pk']
        return reverse('pensionapp:pension_detail', kwargs={'pk': pension_pk})
#
#
class PensionAssetDetailView(DetailView, FormMixin):
    model = PensionAsset
    context_object_name = 'target_pension_asset'
    form_class = PensionAssetTransactionCreationForm
    template_name = 'pensionapp/pensionasset_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionAssetDetailView, self).get_context_data(**kwargs)

        # Update AssetMaster's current price
        self.object.asset_master.update_current_price()
        self.object.asset_master.refresh_from_db()

        # Update PensionAsset's stats
        self.object.update_statistics()
        self.object.refresh_from_db()

        target_pension = self.object.pension
        context.update({'target_pension': target_pension})

        queryset_transaction_list = AssetTransaction.objects.filter(asset=self.object.pk).order_by("-transaction_date")
        for transaction in queryset_transaction_list:
            if transaction.quantity == 0:
                transaction.quantity = '-'
            if transaction.price == 0:
                transaction.price = '-'
            if transaction.transaction_fee == 0:
                transaction.transaction_fee = '-'
            if transaction.transaction_tax == 0:
                transaction.transaction_tax = '-'
            if transaction.dividend_amount == 0:
                transaction.dividend_amount = '-'
            if transaction.split_ratio_one_to_N == 1:
                transaction.split_ratio_one_to_N = '-'
            if transaction.note is None:
                transaction.note = '-'
        context.update({'queryset_transaction_list': queryset_transaction_list})

        context.update({'pension_asset_flag': True})

        return context


class PensionAssetDeleteView(DeleteView):
    model = PensionAsset
    context_object_name = 'target_pension_asset'
    template_name = 'pensionapp/pensionasset_delete.html'

    def get_success_url(self):
        return reverse('pensionapp:pension_detail', kwargs={'pk': self.request.POST['pension_pk']})


class PensionAssetTransactionCreateView(CreateView):
    model = AssetTransaction
    form_class = PensionAssetTransactionCreationForm
    template_name = 'pensionapp/pensionassettransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.asset = PensionAsset.objects.get(pk=self.request.POST['pension_asset_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.asset.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pensionapp:pensionasset_detail', kwargs={'pk': self.object.asset.pk})


class PensionAssetTransactionDeleteView(AssetTransactionDeleteView):
    # model = AssetTransaction
    # context_object_name = 'target_asset_transaction'
    # template_name = 'assetapp/assettransaction_delete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PensionAssetTransactionDeleteView, self).get_context_data(**kwargs)
        context.update({'pension_asset_flag': True})
        return context

    def get_success_url(self):
        return reverse('pensionapp:pensionasset_detail', kwargs={'pk': self.object.asset.pk})
