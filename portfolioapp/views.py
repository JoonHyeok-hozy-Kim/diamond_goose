from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from django.views.generic import CreateView, DetailView, ListView

from assetapp.models import Asset, PensionAsset
from dashboardapp.models import Dashboard
from exchangeapp.models import ForeignCurrency
from masterinfoapp.models import AssetMaster, AssetTypeMaster
from pensionapp.models import Pension
from portfolioapp.decorators import portfolio_ownership_required
from portfolioapp.forms import PortfolioCreationForm
from portfolioapp.models import Portfolio

has_ownership = [login_required, portfolio_ownership_required]


class PortfolioCreateView(CreateView):
    model = Portfolio
    form_class = PortfolioCreationForm
    template_name = 'portfolioapp/portfolio_create.html'

    def form_valid(self, form):
        temp_portfolio = form.save(commit=False)
        temp_portfolio.owner = self.request.user
        temp_portfolio.dashboard = Dashboard.objects.get(pk=self.request.POST['dashboard_pk'])
        temp_portfolio.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboardapp:detail', kwargs={'pk': self.request.POST['dashboard_pk']})


@method_decorator(has_ownership, 'get')
class PortfolioDetailView(DetailView):
    model = Portfolio
    context_object_name = 'target_portfolio'
    template_name = 'portfolioapp/portfolio_detail.html'

    def asset_value_exchanger(self, asset):
        if asset.asset_master.currency.pk == self.object.dashboard.main_currency.pk:
            result = asset.total_amount
        else:
            target_currency_pk = asset.asset_master.currency.pk
            queryset_foreign_currency = ForeignCurrency.objects.get(dashboard=self.object.dashboard.pk,
                                                                    owner=self.request.user,
                                                                    currency_master=target_currency_pk)
            result = asset.total_amount * queryset_foreign_currency.current_exchange_rate
        return result

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)

        # Equity
        queryset_asset_type_master_equity = AssetTypeMaster.objects.get(asset_type_code='EQUITY')
        context.update({'asset_type_master_equity': queryset_asset_type_master_equity})
        queryset_my_equities = Asset.objects.filter(owner=self.request.user,
                                                    portfolio=self.object.pk,
                                                    asset_master__asset_type_master=queryset_asset_type_master_equity.pk,
                                                    position_opened_flag=True).order_by('asset_master__ticker')

        if queryset_my_equities:
            for equity in queryset_my_equities:
                # equity.update_statistics()
                # equity.refresh_from_db()
                equity.total_amount_in_main_currency = self.asset_value_exchanger(equity)
            context.update({'queryset_my_equities': queryset_my_equities})
            context.update({'asset_count_equity': queryset_my_equities.count()+1})

        # Guardian
        queryset_asset_type_master_guardian = AssetTypeMaster.objects.get(asset_type_code='GUARDIAN')
        context.update({'asset_type_master_guardian': queryset_asset_type_master_guardian})
        queryset_my_guardians = Asset.objects.filter(owner=self.request.user,
                                                     portfolio=self.object.pk,
                                                     asset_master__asset_type_master=queryset_asset_type_master_guardian,
                                                     position_opened_flag=True).order_by('asset_master__ticker')
        if queryset_my_guardians:
            for guardian in queryset_my_guardians:
                # guardian.update_statistics()
                # guardian.refresh_from_db()
                guardian.total_amount_in_main_currency = self.asset_value_exchanger(guardian)
            context.update({'queryset_my_guardians': queryset_my_guardians})
            context.update({'asset_count_guardians': queryset_my_guardians.count()+1})

        # Reits
        queryset_asset_type_master_reits = AssetTypeMaster.objects.get(asset_type_code='REITS')
        context.update({'asset_type_master_reits': queryset_asset_type_master_reits})
        queryset_my_reits = Asset.objects.filter(owner=self.request.user,
                                                 portfolio=self.object.pk,
                                                 asset_master__asset_type_master=queryset_asset_type_master_reits,
                                                 position_opened_flag=True).order_by('asset_master__ticker')
        if queryset_my_reits:
            for reits in queryset_my_reits:
                # reits.update_statistics()
                # reits.refresh_from_db()
                reits.total_amount_in_main_currency = self.asset_value_exchanger(reits)
            context.update({'queryset_my_reits': queryset_my_reits})
            context.update({'asset_count_reits': queryset_my_reits.count()+1})

        # Crypto
        queryset_asset_type_master_crypto = AssetTypeMaster.objects.get(asset_type_code='CRYPTO')
        context.update({'asset_type_master_crypto': queryset_asset_type_master_crypto})
        queryset_my_crypto = Asset.objects.filter(owner=self.request.user,
                                                  portfolio=self.object.pk,
                                                  asset_master__asset_type_master=queryset_asset_type_master_crypto,
                                                  position_opened_flag=True).order_by('asset_master__ticker')
        if queryset_my_crypto:
            for crypto in queryset_my_crypto:
                # crypto.update_statistics()
                # crypto.refresh_from_db()
                crypto.total_amount_in_main_currency = self.asset_value_exchanger(crypto)
            context.update({'queryset_my_crypto': queryset_my_crypto})
            context.update({'asset_count_crypto': queryset_my_crypto.count()+1})

        # Pension
        queryset_asset_type_master_pension_asset = AssetTypeMaster.objects.get(asset_type_code='PENSION_ASSET')
        context.update({'asset_type_master_pension_asset': queryset_asset_type_master_pension_asset})

        queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user,
                                                                 portfolio=self.object.pk,
                                                                 asset_master__asset_type_master=queryset_asset_type_master_pension_asset,
                                                                 position_opened_flag=True).order_by('pension',
                                                                                                     'asset_master__name')

        if queryset_my_pension_assets:

            for pension_asset in queryset_my_pension_assets:
                # pension_asset.update_statistics()
                # pension_asset.refresh_from_db()
                pension_asset.total_amount_in_main_currency = self.asset_value_exchanger(pension_asset)
            context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
            context.update({'asset_count_pension': queryset_my_pension_assets.count()+1})


        # queryset_my_pensions = Pension.objects.filter(owner=self.request.user,
        #                                               portfolio=self.object.pk)
        # pension_asset_list = []
        # pension_total_line_count = 1
        # for pension in queryset_my_pensions:
        #     queryset_pension_asset = PensionAsset.objects.filter(owner=self.request.user,
        #                                                          pension=pension.pk,
        #                                                          portfolio=self.object.pk,
        #                                                          position_opened_flag=True)
        #     for pension_asset in queryset_pension_asset:
        #         pension_asset.total_amount_in_main_currency = self.asset_value_exchanger(pension_asset)
        #     pension_asset_list.append(queryset_pension_asset)
        #     pension_total_line_count += queryset_pension_asset.count()
        # context.update({'asset_count_pension': pension_total_line_count})
        # if len(pension_asset_list) > 0:
        #     context.update({'pension_asset_list': pension_asset_list})

        # Update Statistics
        self.object.update_statistics(price_update=False)

        return context


@method_decorator(has_ownership, 'get')
class PortfolioDetailViewIncludeClosed(DetailView):
    model = Portfolio
    context_object_name = 'target_portfolio'
    template_name = 'portfolioapp/portfolio_detail.html'

    def asset_value_exchanger(self, asset):
        if asset.asset_master.currency.pk == self.object.dashboard.main_currency.pk:
            result = asset.total_amount
        else:
            target_currency_pk = asset.asset_master.currency.pk
            queryset_foreign_currency = ForeignCurrency.objects.get(dashboard=self.object.dashboard.pk,
                                                                    owner=self.request.user,
                                                                    currency_master=target_currency_pk)
            result = asset.total_amount * queryset_foreign_currency.current_exchange_rate
        return result

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailViewIncludeClosed, self).get_context_data(**kwargs)

        # Equity
        queryset_asset_type_master_equity = AssetTypeMaster.objects.get(asset_type_code='EQUITY')
        context.update({'asset_type_master_equity': queryset_asset_type_master_equity})
        queryset_my_equities = Asset.objects.filter(owner=self.request.user,
                                                    portfolio=self.object.pk,
                                                    asset_master__asset_type_master=queryset_asset_type_master_equity.pk).order_by('-position_opened_flag',
                                                                                                                                   'asset_master__ticker')
        if queryset_my_equities:
            for equity in queryset_my_equities:
                # equity.update_statistics()
                # equity.refresh_from_db()
                equity.total_amount_in_main_currency = self.asset_value_exchanger(equity)
            context.update({'queryset_my_equities': queryset_my_equities})
            context.update({'asset_count_equity': queryset_my_equities.count()+1})

        # Guardian
        queryset_asset_type_master_guardian = AssetTypeMaster.objects.get(asset_type_code='GUARDIAN')
        context.update({'asset_type_master_guardian': queryset_asset_type_master_guardian})
        queryset_my_guardians = Asset.objects.filter(owner=self.request.user,
                                                     portfolio=self.object.pk,
                                                     asset_master__asset_type='GUARDIAN').order_by('-position_opened_flag',
                                                                                                   'asset_master__ticker')
        if queryset_my_guardians:
            for guardian in queryset_my_guardians:
                # guardian.update_statistics()
                # guardian.refresh_from_db()
                guardian.total_amount_in_main_currency = self.asset_value_exchanger(guardian)
            context.update({'queryset_my_guardians': queryset_my_guardians})
            context.update({'asset_count_guardians': queryset_my_guardians.count()+1})

        # Reits
        queryset_asset_type_master_reits = AssetTypeMaster.objects.get(asset_type_code='REITS')
        context.update({'asset_type_master_reits': queryset_asset_type_master_reits})
        queryset_my_reits = Asset.objects.filter(owner=self.request.user,
                                                 portfolio=self.object.pk,
                                                 asset_master__asset_type='REITS').order_by('-position_opened_flag',
                                                                                            'asset_master__ticker')
        if queryset_my_reits:
            for reits in queryset_my_reits:
                # reits.update_statistics()
                # reits.refresh_from_db()
                reits.total_amount_in_main_currency = self.asset_value_exchanger(reits)
            context.update({'queryset_my_reits': queryset_my_reits})
            context.update({'asset_count_reits': queryset_my_reits.count()+1})

        # Crypto
        queryset_asset_type_master_crypto = AssetTypeMaster.objects.get(asset_type_code='CRYPTO')
        context.update({'asset_type_master_crypto': queryset_asset_type_master_crypto})
        queryset_my_crypto = Asset.objects.filter(owner=self.request.user,
                                                  portfolio=self.object.pk,
                                                  asset_master__asset_type='CRYPTO').order_by('-position_opened_flag',
                                                                                              'asset_master__ticker')
        if queryset_my_crypto:
            for crypto in queryset_my_crypto:
                # crypto.update_statistics()
                # crypto.refresh_from_db()
                crypto.total_amount_in_main_currency = self.asset_value_exchanger(crypto)
            context.update({'queryset_my_crypto': queryset_my_crypto})
            context.update({'asset_count_crypto': queryset_my_crypto.count()+1})

        # Pension
        queryset_asset_type_master_pension_asset = AssetTypeMaster.objects.get(asset_type_code='PENSION_ASSET')
        context.update({'asset_type_master_pension_asset': queryset_asset_type_master_pension_asset})
        queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user,
                                                                 portfolio=self.object.pk,
                                                                 asset_master__asset_type='PENSION_ASSET').order_by('pension',
                                                                                                                    '-position_opened_flag',
                                                                                                                    'asset_master__name')

        if queryset_my_pension_assets:
            for pension_asset in queryset_my_pension_assets:
                # pension_asset.update_statistics()
                # pension_asset.refresh_from_db()
                pension_asset.total_amount_in_main_currency = self.asset_value_exchanger(pension_asset)
            context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
            context.update({'asset_count_pension': queryset_my_pension_assets.count()+1})

        # Update Statistics
        self.object.update_statistics(price_update=False)
        context.update({'closed_asset_include_flag': True})

        return context


class PortfolioAssetMasterListView(ListView):
    model = AssetMaster
    template_name = 'masterinfoapp/assetmaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PortfolioAssetMasterListView, self).get_context_data(**kwargs)

        try:
            queryset_my_portfolio = Portfolio.objects.get(owner=self.request.user)
            my_portfolio_pk = queryset_my_portfolio.pk

        except Exception as identifier:
            print('ProfileAssetMasterDetailView queryset_my_portfolio Exception : {}'.format(identifier))

        query_asset_master_list = AssetMaster.objects.exclude(id__in=Asset.objects.filter(portfolio=my_portfolio_pk).values('asset_master_id')).exclude(asset_type='PENSION_ASSET').order_by('asset_type', 'ticker')
        for asset_master in query_asset_master_list:
            asset_master.name = Truncator(asset_master.name).chars(29)
        context.update({'query_asset_master_list': query_asset_master_list})

        context.update({'portfolio_assetmaster_list_flag': True})

        return context


class PortfolioAssetMasterDetailView(DetailView):
    model = AssetMaster
    context_object_name = 'target_asset_master'
    template_name = 'portfolioapp/portfolio_assetmaster_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.update_current_price()
        self.object.refresh_from_db()

        context = super(PortfolioAssetMasterDetailView, self).get_context_data(**kwargs)

        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'portfolio_assetmaster_detail_flag': True})

        return context


def portfolio_refresh(request):

    try:
        queryset_my_portfolio = Portfolio.objects.get(owner=request.user)
        queryset_my_portfolio.update_statistics(price_update=True)

    except Exception as identifier:
        print('portfolio_refresh:', identifier)

    return redirect('portfolioapp:portfolio_detail', pk=queryset_my_portfolio.pk)

