# Generated by Django 3.2.11 on 2022-02-07 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterinfoapp', '0011_assetmaster_asset_type_master'),
    ]

    operations = [
        migrations.AddField(
            model_name='assettypemaster',
            name='asset_type_name_full',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='assetmaster',
            name='asset_type',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
