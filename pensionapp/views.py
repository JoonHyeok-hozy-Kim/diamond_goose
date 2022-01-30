import json

from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin, DeleteView

from dashboardapp.models import Dashboard
from pensionapp.forms import PensionCreationForm, PensionTransactionCreationForm
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
        self.object.update_parameters()
        self.object.refresh_from_db()

        context.update({'my_pension_pk': self.object.pk})

        # pension_asset_list = PensionAsset.objects.filter(pension=self.object.pk)
        # context.update({'pension_asset_list': pension_asset_list})

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

        temp_pension_transaction.pension.calculate_total_paid_amount()

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


# class PensionAssetListView(ListView):
#     model = Asset
#     context_object_name = 'target_asset_list'
#     template_name = 'pensionapp/pensionasset_list.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super(PensionAssetListView, self).get_context_data(**kwargs)
#
#         request_dict = self.request.__dict__
#         # Get asset_pk info from the path
#         pension_pk = request_dict['path'].split('/')[-1]
#         context.update({'pension_pk': pension_pk})
#
#         queryset_my_pension_asset = PensionAsset.objects.filter(pension=pension_pk).values()
#         my_pension_asset_list = []
#         for pension_asset in queryset_my_pension_asset:
#             my_pension_asset_list.append(pension_asset['asset_id'])
#         queryset_not_my_pension_asset_asset = Asset.objects.exclude(id__in=my_pension_asset_list).filter(asset_type='PENSION').values()
#
#         for query_pension_asset in queryset_not_my_pension_asset_asset:
#             from django.utils.text import Truncator
#             query_pension_asset['name'] = Truncator(query_pension_asset['name']).chars(29)
#             query_pension_asset['image'] = 'media/'+query_pension_asset['image']
#
#         context.update({'queryset_not_my_pension_asset_asset': queryset_not_my_pension_asset_asset})
#         return context
#
#
# class PensionAssetCreateView(CreateView):
#     model = PensionAsset
#     template_name = 'pensionapp/pensionasset_create.html'
#     form_class = PensionAssetCreationForm
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super(PensionAssetCreateView, self).get_context_data(**kwargs)
#
#         request_dict = self.request.__dict__['path'].split('/')
#         # Get asset_pk info from the path
#         pension_pk = request_dict[-2]
#         query_set_target_pension = Pension.objects.filter(pk=pension_pk).values()
#         target_pension_pk = query_set_target_pension[0]['id']
#         context.update({'target_pension': target_pension_pk})
#
#         asset_pk = request_dict[-1]
#         target_asset = Asset.objects.get(pk=asset_pk)
#         context.update({'target_asset': target_asset})
#
#         return context
#
#     def form_valid(self, form):
#         temp_pension_asset = form.save(commit=False)
#         temp_pension_asset.owner = self.request.user
#
#         # Get asset_pk and pension_pk from request URL
#         request_dict = self.request.__dict__['path'].split('/')
#         asset_pk = request_dict[-1]
#         temp_pension_asset.asset = Asset.objects.get(pk=asset_pk)
#
#         pension_pk = request_dict[-2]
#         temp_pension_asset.pension = Pension.objects.get(pk=pension_pk)
#         temp_pension_asset.save()
#
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         pension_pk = self.request.__dict__['path'].split('/')[-2]
#         return reverse('pensionapp:pension_detail', kwargs={'pk': pension_pk})
#
#
# class PensionAssetDeleteView(DeleteView):
#     model = PensionAsset
#     context_object_name = 'target_pension_asset'
#     template_name = 'pensionapp/pensionasset_delete.html'
#
#     def get_success_url(self):
#         return reverse('pensionapp:pension_detail', kwargs={'pk': self.request.POST['pension_pk']})
#
#
# class PensionAssetDetailView(DetailView, FormMixin):
#     model = PensionAsset
#     context_object_name = 'target_pension_asset'
#     form_class = PensionAssetTransactionCreationForm
#     template_name = 'pensionapp/pensionasset_detail.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super(PensionAssetDetailView, self).get_context_data(**kwargs)
#         # Update Asset's current price
#         self.object.asset.update_current_price()
#         self.object.asset.refresh_from_db()
#
#         # Update Pension Asset's stats
#         self.object.update_pension_asset_data()
#         self.object.refresh_from_db()
#
#         target_pension = self.object.pension
#         context.update({'target_pension': target_pension})
#
#         queryset_transaction_list = PensionAssetTransaction.objects.filter(pension_asset=self.object.pk).order_by("-transaction_date")
#         context.update({'queryset_transaction_list': queryset_transaction_list})
#
#         return context
#
#
# class PensionAssetTransactionCreateView(CreateView):
#     model = PensionAssetTransaction
#     form_class = PensionAssetTransactionCreationForm
#     template_name = 'pensionapp/pensionassettransaction_create.html'
#
#     def form_valid(self, form):
#         temp_transaction = form.save(commit=False)
#         temp_transaction.pension_asset = PensionAsset.objects.get(pk=self.request.POST['pension_asset_pk'])
#
#         if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.pension_asset.quantity:
#             return HttpResponseNotFound('Cannot SELL more than you hold.')
#
#         temp_transaction.save()
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse('pensionapp:pensionasset_detail', kwargs={'pk': self.object.pension_asset.pk})
#
#
# class PensionAssetTransactionDeleteView(DeleteView):
#     model = PensionAssetTransaction
#     context_object_name = 'target_pension_asset_transaction'
#     template_name = 'pensionapp/pensionassettransaction_delete.html'
#
#     def get_success_url(self):
#         return reverse('pensionapp:pensionasset_detail', kwargs={'pk': self.object.pension_asset.pk})
