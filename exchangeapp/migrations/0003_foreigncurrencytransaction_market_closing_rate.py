# Generated by Django 3.2.11 on 2022-02-09 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchangeapp', '0002_foreigncurrency_total_realized_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='foreigncurrencytransaction',
            name='market_closing_rate',
            field=models.FloatField(null=True),
        ),
    ]
