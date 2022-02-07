# Generated by Django 3.2.11 on 2022-01-31 02:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pensionapp', '0004_pension_total_received_amount'),
        ('assetapp', '0002_assettransaction_asset'),
    ]

    operations = [
        migrations.CreateModel(
            name='PensionAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='assetapp.asset')),
                ('pension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pension_asset', to='pensionapp.pension')),
            ],
            bases=('assetapp.asset',),
        ),
    ]