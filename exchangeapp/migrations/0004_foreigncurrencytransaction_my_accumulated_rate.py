# Generated by Django 3.2.11 on 2022-02-10 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchangeapp', '0003_foreigncurrencytransaction_market_closing_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='foreigncurrencytransaction',
            name='my_accumulated_rate',
            field=models.FloatField(null=True),
        ),
    ]
