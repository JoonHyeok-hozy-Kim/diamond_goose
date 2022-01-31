# Generated by Django 3.2.11 on 2022-01-31 09:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('masterinfoapp', '0002_alter_assetmaster_asset_type'),
        ('dashboardapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ForeignCurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_amount', models.FloatField(default=0)),
                ('current_exchange_rate', models.FloatField(default=0)),
                ('accumulated_exchange_rate_mv', models.FloatField(default=0)),
                ('accumulated_exchange_rate_fifo', models.FloatField(default=0)),
                ('rate_of_return_mv', models.FloatField(default=0)),
                ('rate_of_return_fifo', models.FloatField(default=0)),
                ('currency_master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foreign_currency', to='masterinfoapp.currencymaster')),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foreign_currency', to='dashboardapp.dashboard')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foreign_currency', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForeignCurrencyTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('BUY', '매수'), ('SELL', '매도')], max_length=20)),
                ('amount', models.FloatField(default=0)),
                ('exchange_rate', models.FloatField(default=0)),
                ('applied_flag', models.BooleanField(default=False)),
                ('note', models.CharField(default='-', max_length=100, null=True)),
                ('transaction_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
                ('foreign_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='exchangeapp.foreigncurrency')),
            ],
        ),
    ]
