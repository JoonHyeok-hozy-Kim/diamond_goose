from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from django.views.generic import CreateView, DetailView, ListView

from dashboardapp.models import Dashboard
from masterinfoapp.models import AssetMaster
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

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)

        # queryset_my_equities = Equity.objects.filter(owner=self.request.user,
        #                                              portfolio=self.object.pk,
        #                                              asset_master__asset_type='EQUITY')
        # if queryset_my_equities:
        #     for equity in queryset_my_equities:
        #         equity.update_statistics()
        #     context.update({'asset_model_equity': 'Equity'})
        #     context.update({'queryset_my_equities': queryset_my_equities})
        #     context.update({'asset_count_equity': queryset_my_equities.count()+1})
        #
        # queryset_my_guardians = Equity.objects.filter(owner=self.request.user,
        #                                               portfolio=self.object.pk,
        #                                               asset_master__asset_type='GUARDIAN')
        # if queryset_my_guardians:
        #     for guardian in queryset_my_guardians:
        #         guardian.update_statistics()
        #     context.update({'asset_model_guardian': 'Guardian'})
        #     context.update({'queryset_my_guardians': queryset_my_guardians})
        #     context.update({'asset_count_guardians': queryset_my_guardians.count()+1})
        #
        # queryset_my_reits = Equity.objects.filter(owner=self.request.user,
        #                                           portfolio=self.object.pk,
        #                                           asset_master__asset_type='REITS')
        # if queryset_my_reits:
        #     for reits in queryset_my_reits:
        #         reits.update_statistics()
        #     context.update({'asset_model_reits': 'Reits'})
        #     context.update({'queryset_my_reits': queryset_my_reits})
        #     context.update({'asset_count_reits': queryset_my_reits.count()+1})

        # for element in asset_type_count_list:
        #
        #     elif element['asset_type'] == 'CRYPTO':
        #         queryset_my_cryptoes = Crypto.objects.filter(owner=self.request.user).order_by("asset")
        #         context.update({'queryset_my_cryptoes': queryset_my_cryptoes})
        #         context.update({'asset_count_cryptoes': element['asset_count'] + 1})
        #
        #     elif element['asset_type'] == 'PENSION':
        #         queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user).order_by('pension')
        #         context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
        #         context.update({'asset_count_pension_asset': element['asset_count'] + 1})

        return context


class ProfileAssetMasterListView(ListView):
    model = AssetMaster
    template_name = 'masterinfoapp/assetmaster_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProfileAssetMasterListView, self).get_context_data(**kwargs)

        try:
            queryset_my_portfolio = Portfolio.objects.get(owner=self.request.user)
            my_portfolio_pk = queryset_my_portfolio.pk
            target_user_id = queryset_my_portfolio.id

        except Exception as identifier:
            print('ProfileAssetMasterDetailView queryset_my_portfolio Exception : {}'.format(identifier))

        query_asset_master_list = AssetMaster.objects.all().order_by('asset_type', 'ticker')
        # query_asset_master_list = AssetMaster.objects.exclude(id__in=Equity.objects.filter(portfolio=my_portfolio_pk).values('asset_master_id')).order_by('asset_type', 'ticker')
        for asset_master in query_asset_master_list:
            asset_master.name = Truncator(asset_master.name).chars(29)
        context.update({'query_asset_master_list': query_asset_master_list})

        context.update({'profile_assetmaster_list_flag': True})

        return context


class ProfileAssetMasterDetailView(DetailView):
    model = AssetMaster
    context_object_name = 'target_asset_master'
    template_name = 'portfolioapp/portfolio_assetmaster_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.update_current_price()
        self.object.refresh_from_db()

        context = super(ProfileAssetMasterDetailView, self).get_context_data(**kwargs)

        context.update({'default_image_url': 'static/images/diamond_goose_logo_mk1.png'})
        context.update({'profile_assetmaster_detail_flag': True})

        # if self.request.user.is_authenticated:
        #
        #     try:
        #         queryset_my_portfolio = Portfolio.objects.get(owner=self.request.user)
        #         my_portfolio_pk = queryset_my_portfolio.pk
        #         target_user_id = queryset_my_portfolio.id
        #
        #         my_asset_pk = None
        #         if self.object.asset_type in ['EQUITY', 'GUARDIAN', 'REITS']:
        #             context.update({'asset_model': 'EQUITY'})
        #             try:
        #                 queryset_my_equity = Equity.objects.get(asset_master=self.object.pk,
        #                                                         portfolio=my_portfolio_pk,
        #                                                         owner=target_user_id)
        #                 my_asset_pk = queryset_my_equity.pk
        #             except Exception as identifier:
        #                 print('ProfileAssetMasterDetailView queryset_my_equity Exception : {}'.format(identifier))
        #
        #         elif self.object.asset_type == 'CRYPTO':
        #             None
        #
        #         elif self.object.asset_type == 'PENSION':
        #             None
        #
        #     except Exception as identifier:
        #         print('ProfileAssetMasterDetailView queryset_my_portfolio Exception : {}'.format(identifier))
        #
        #
        #     # my_portfolio_scalar_query = Portfolio.objects.filter(owner=self.request.user).values()
        #     # if my_portfolio_scalar_query:
        #     #     for my_portfolio in my_portfolio_scalar_query:
        #     #         my_portfolio_pk = my_portfolio['id']
        #     #         target_user_id = my_portfolio['owner_id']
        #     #     context.update({'my_portfolio_pk': my_portfolio_pk})
        #     #     context.update({'target_user_id': target_user_id})
        #     #
        #     #     my_asset_pk = None
        #     #     if self.object.asset_type == 'EQUITY':
        #     #         my_equity_scalar_query = Equity.objects.filter(asset=self.object.pk,
        #     #                                                        portfolio=my_portfolio_pk,
        #     #                                                        owner=self.request.user).values()
        #     #         if my_equity_scalar_query:
        #     #             for my_equity in my_equity_scalar_query:
        #     #                 my_asset_pk = my_equity['asset_id']
        #     #
        #     #     elif self.object.asset_type == 'GUARDIAN':
        #     #         queryset_my_guardian = Guardian.objects.filter(asset=self.object.pk,
        #     #                                                        portfolio=my_portfolio_pk,
        #     #                                                        owner=self.request.user)
        #     #         if queryset_my_guardian:
        #     #             for my_guardian in queryset_my_guardian:
        #     #                 my_asset_pk = my_guardian.asset.pk
        #     #
        #     #     elif self.object.asset_type == 'REITS':
        #     #         queryset_my_reits = Reits.objects.filter(asset=self.object.pk,
        #     #                                                  portfolio=my_portfolio_pk,
        #     #                                                  owner=self.request.user)
        #     #         if queryset_my_reits:
        #     #             for my_guardian in queryset_my_reits:
        #     #                 my_asset_pk = my_guardian.asset.pk
        #     #
        #     #     elif self.object.asset_type == 'PENSION':
        #     #         None
        #     #
        #     #     elif self.object.asset_type == 'CRYPTO':
        #     #         queryset_my_crypto = Crypto.objects.filter(asset=self.object.pk,
        #     #                                                    portfolio=my_portfolio_pk,
        #     #                                                    owner=self.request.user)
        #     #         if queryset_my_crypto:
        #     #             for my_crypto in queryset_my_crypto:
        #     #                 my_asset_pk = my_crypto.asset.pk
        #     #
        #     if my_asset_pk:
        #         context.update({'my_asset_pk': my_asset_pk})

        return context

