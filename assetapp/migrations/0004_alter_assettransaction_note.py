# Generated by Django 3.2.11 on 2022-01-31 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetapp', '0003_pensionasset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assettransaction',
            name='note',
            field=models.CharField(default='-', max_length=100, null=True),
        ),
    ]
