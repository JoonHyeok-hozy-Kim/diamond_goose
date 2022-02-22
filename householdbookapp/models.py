import datetime

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dashboardapp.models import Dashboard
from exchangeapp.models import ForeignCurrency
from masterinfoapp.models import CurrencyMaster

liquidity_type_list = (
    ('DEPOSIT', 'Bank Deposit'),
    ('CMA', "IB's CMA"),
    ('INSTALLMENT', 'Installment Saving'),
    ('VOUCHER', 'Voucher'),
    ('FOREIGN_CURRENCY', 'Foreign Currency'),
)


class Liquidity(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liquidity')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='liquidity')
    liquidity_type = models.CharField(max_length=100, choices=liquidity_type_list, null=False)
    liquidity_name = models.CharField(max_length=100, default='Liquidity', null=False)
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.CASCADE, related_name='liquidity')
    amount = models.FloatField(default=0, null=False)
    amount_exchanged = models.FloatField(default=0, null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_statistics(self):
        self.amount_exchanged_calculation()
        self.refresh_from_db()

    def amount_exchanged_calculation(self):
        queryset_my_foreign_currencies = ForeignCurrency.objects.filter(owner=self.owner,
                                                                        dashboard=self.dashboard)
        target_liquidity = Liquidity.objects.filter(pk=self.pk)
        for foreign_currency in queryset_my_foreign_currencies:
            if self.currency == foreign_currency.currency_master:
                foreign_currency.update_statistics()
                foreign_currency.refresh_from_db()
                amount_exchanged = self.amount * foreign_currency.current_exchange_rate
                target_liquidity.update(amount_exchanged=amount_exchanged)
                return
        target_liquidity.update(amount_exchanged=self.amount)


class Debt(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debt')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='debt')
    debt_name = models.CharField(max_length=100, default='debt', null=False)
    long_term_debt_flag = models.BooleanField(default=False, null=False)
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.CASCADE, related_name='debt')
    amount = models.FloatField(default=0, null=False)
    amount_exchanged = models.FloatField(default=0, null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_statistics(self):
        self.amount_exchanged_calculation()
        self.refresh_from_db()

    def amount_exchanged_calculation(self):
        queryset_my_foreign_currencies = ForeignCurrency.objects.filter(owner=self.owner,
                                                                        dashboard=self.dashboard)
        target_debt = Debt.objects.filter(pk=self.pk)
        for foreign_currency in queryset_my_foreign_currencies:
            if self.currency == foreign_currency.currency_master:
                foreign_currency.update_statistics()
                foreign_currency.refresh_from_db()
                amount_exchanged = self.amount * foreign_currency.current_exchange_rate
                target_debt.update(amount_exchanged=amount_exchanged)
                return
        target_debt.update(amount_exchanged=self.amount)


class IncomeExpense(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_expense')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='income_expense')
    period_name = models.CharField(max_length=10, null=False)

    total_income_amount = models.FloatField(default=0, null=False)
    income_labor = models.FloatField(default=0, null=False)
    income_capital = models.FloatField(default=0, null=False)
    income_etc = models.FloatField(default=0, null=False)

    total_expense_amount = models.FloatField(default=0, null=False)
    expense_housing_communication = models.FloatField(default=0, null=False)
    expense_living = models.FloatField(default=0, null=False)
    expense_grocery = models.FloatField(default=0, null=False)
    expense_shopping = models.FloatField(default=0, null=False)
    expense_leisure = models.FloatField(default=0, null=False)
    expense_health = models.FloatField(default=0, null=False)
    expense_largess = models.FloatField(default=0, null=False)
    expense_transportation = models.FloatField(default=0, null=False)
    expense_alcohol = models.FloatField(default=0, null=False)
    expense_education = models.FloatField(default=0, null=False)
    expense_car = models.FloatField(default=0, null=False)
    expense_financial = models.FloatField(default=0, null=False)
    expense_love_affair = models.FloatField(default=0, null=False)
    expense_etc = models.FloatField(default=0, null=False)

    total_savings_amount = models.FloatField(default=0, null=False)
    monthly_savings_rate = models.FloatField(default=0, null=False)

    def update_statistics(self):
        target_income_expense = IncomeExpense.objects.filter(pk=self.pk)
        target_income_expense.update(
            total_income_amount=sum([
                self.income_labor,
                self.income_capital,
                self.income_etc,
            ]),
            total_expense_amount=sum([
                self.expense_housing_communication,
                self.expense_living,
                self.expense_grocery,
                self.expense_shopping,
                self.expense_leisure,
                self.expense_health,
                self.expense_largess,
                self.expense_transportation,
                self.expense_alcohol,
                self.expense_education,
                self.expense_car,
                self.expense_financial,
                self.expense_love_affair,
                self.expense_etc,
            ]),
            total_savings_amount=self.total_income_amount-self.total_expense_amount
        )

        if sum([self.income_labor, self.income_capital, self.income_etc]) > 0:
            target_income_expense.update(monthly_savings_rate=self.total_savings_amount/sum([self.income_labor, self.income_capital, self.income_etc]))


class BuyNowPayLater(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_now_pay_later')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='buy_now_pay_later')
    currency = models.ForeignKey(CurrencyMaster, on_delete=models.CASCADE, related_name='buy_now_pay_later')
    item_name = models.CharField(max_length=100, null=False)
    total_amount = models.FloatField(default=0, null=False)
    discount_amount = models.FloatField(default=0, null=False)
    purchase_period = models.CharField(max_length=10, null=False)
    paying_months = models.FloatField(default=0, null=False)
    note = models.CharField(max_length=200, null=True)

    current_payment_count = models.FloatField(default=0, null=False)
    nominal_remaining_amount = models.FloatField(default=0, null=False)
    nominal_monthly_payment_amount = models.FloatField(default=0, null=False)
    real_remaining_amount = models.FloatField(default=0, null=False)
    real_monthly_payment_amount = models.FloatField(default=0, null=False)
    end_flag = models.BooleanField(default=False, null=False)

    def update_statistics(self):
        target_bnpl = BuyNowPayLater.objects.filter(pk=self.pk)

        # current_payment_count
        todays_year = int(datetime.datetime.today().strftime('%Y'))
        todays_month = int(datetime.datetime.today().strftime('%m'))
        purchase_year = int(self.purchase_period.split('-')[0])
        purchase_month = int(self.purchase_period.split('-')[1])
        month_diff = (todays_year-purchase_year)*12 + (todays_month-purchase_month) + 1
        if month_diff > self.paying_months:
            current_payment_count=self.paying_months
        else:
            current_payment_count=month_diff
        target_bnpl.update(current_payment_count=current_payment_count)

        if month_diff > self.paying_months+1:
            target_bnpl.update(end_flag=True)
        else:
            target_bnpl.update(end_flag=False)

        nominal_monthly_payment_amount = self.total_amount/self.paying_months
        target_bnpl.update(nominal_monthly_payment_amount=nominal_monthly_payment_amount)
        nominal_remaining_amount = self.total_amount - nominal_monthly_payment_amount*current_payment_count
        target_bnpl.update(nominal_remaining_amount=nominal_remaining_amount)

        real_purchase_amount = self.total_amount-self.discount_amount
        real_monthly_payment_amount = real_purchase_amount/self.paying_months
        target_bnpl.update(real_monthly_payment_amount=real_monthly_payment_amount)
        real_remaining_amount = real_purchase_amount - real_monthly_payment_amount*current_payment_count
        target_bnpl.update(real_remaining_amount=real_remaining_amount)





