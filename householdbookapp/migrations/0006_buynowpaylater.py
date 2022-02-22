# Generated by Django 3.2.11 on 2022-02-22 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('householdbookapp', '0005_alter_incomeexpense_period_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyNowPayLater',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('total_amount', models.FloatField(default=0)),
                ('discount_amount', models.FloatField(default=0)),
                ('purchase_period', models.CharField(max_length=10)),
                ('paying_months', models.FloatField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('current_payment_count', models.FloatField(default=0)),
                ('nominal_remaining_amount', models.FloatField(default=0)),
                ('real_remaining_amount', models.FloatField(default=0)),
                ('real_monthly_payment_amount', models.FloatField(default=0)),
                ('end_flag', models.BooleanField(default=False)),
            ],
        ),
    ]
