# Generated by Django 3.2.11 on 2022-02-07 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterinfoapp', '0006_assetmaster_etf_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='pensionmaster',
            name='color_hex',
            field=models.CharField(default='#00C483', max_length=7, null=True),
        ),
    ]