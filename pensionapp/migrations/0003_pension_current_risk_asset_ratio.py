# Generated by Django 3.2.11 on 2022-01-30 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pensionapp', '0002_auto_20220131_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='pension',
            name='current_risk_asset_ratio',
            field=models.FloatField(default=0),
        ),
    ]
