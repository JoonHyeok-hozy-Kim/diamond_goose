# Generated by Django 3.2.11 on 2022-02-08 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterinfoapp', '0012_auto_20220207_2127'),
        ('pensionapp', '0005_pension_net_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='pension',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pension', to='masterinfoapp.currencymaster'),
        ),
    ]
