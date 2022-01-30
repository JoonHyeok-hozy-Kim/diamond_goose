from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import FormMixin, DeleteView

from assetapp.decorators import asset_ownership_required
from assetapp.forms import AssetCreationForm, AssetTransactionCreationForm
from assetapp.models import Asset, AssetTransaction
from masterinfoapp.models import AssetMaster
from portfolioapp.models import Portfolio

has_asset_ownership = [login_required, asset_ownership_required]


class AssetCreateView(CreateView):
    model = Asset
    form_class = AssetCreationForm
    context_object_name = 'target_asset'
    template_name = 'assetapp/asset_create.html'

    def form_valid(self, form):
        temp_asset = form.save(commit=False)
        temp_asset.owner = self.request.user
        temp_asset.asset_master = AssetMaster.objects.get(pk=self.request.POST['asset_pk'])
        temp_asset.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_asset.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('portfolioapp:portfolio_detail', kwargs={'pk': self.object.portfolio.pk})
        # return reverse('assetapp:asset_detail', kwargs={'pk': self.object.pk})


@method_decorator(has_asset_ownership, 'get')
class AssetDetailView(DetailView, FormMixin):
    model = Asset
    form_class = AssetTransactionCreationForm
    context_object_name = 'target_asset'
    template_name = 'assetapp/asset_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset_master.update_current_price()
        self.object.asset_master.refresh_from_db()

        # Update Equity's stats
        self.object.update_statistics()

        context = super(AssetDetailView, self).get_context_data(**kwargs)

        my_portfolio_pk = self.object.portfolio.pk
        context.update({'my_portfolio_pk': my_portfolio_pk})

        my_asset_transactions = AssetTransaction.objects.filter(asset=self.object.pk).order_by('-transaction_date')
        for transaction in my_asset_transactions:
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
        context.update({'my_asset_transactions': my_asset_transactions})

        return context


class AssetDeleteView(DeleteView):
    model = Asset
    context_object_name = 'target_asset'
    template_name = 'assetapp/asset_delete.html'

    def get_success_url(self):
        return reverse('portfolioapp:portfolio_detail', kwargs={'pk': self.object.portfolio.pk})


class AssetTransactionCreateView(CreateView):
    model = AssetTransaction
    form_class = AssetTransactionCreationForm
    template_name = 'assetapp/assettransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.asset = Asset.objects.get(pk=self.request.POST['asset_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.asset.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('assetapp:asset_detail', kwargs={'pk': self.object.asset.pk})


class AssetTransactionDeleteView(DeleteView):
    model = AssetTransaction
    context_object_name = 'target_asset_transaction'
    template_name = 'assetapp/assettransaction_delete.html'

    def get_success_url(self):
        print('before reverse, asset : {}'.format(self.object.asset))
        return reverse('assetapp:asset_detail', kwargs={'pk': self.object.asset.pk})



def assettransaction_delete_all(request):

    asset_pk = request.GET['asset_pk']
    queryset_asset_transactions = AssetTransaction.objects.filter(asset=asset_pk)
    delete_count = 0
    asset_name = None
    for transaction in queryset_asset_transactions:
        delete_count += 1
        asset_name = transaction.asset.asset_master.name
        transaction.delete()
    print('Delete transaction of {}. {} row(s) deleted.'.format(asset_name, delete_count))

    target_asset = Asset.objects.get(pk=asset_pk)
    target_asset.update_statistics()

    return HttpResponseRedirect(reverse('assetapp:asset_detail', kwargs={'pk': asset_pk}))