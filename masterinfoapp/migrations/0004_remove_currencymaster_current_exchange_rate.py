# Generated by Django 3.2.11 on 2022-01-31 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('masterinfoapp', '0003_currencymaster_current_exchange_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currencymaster',
            name='current_exchange_rate',
        ),
    ]