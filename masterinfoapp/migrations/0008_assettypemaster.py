# Generated by Django 3.2.11 on 2022-02-07 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterinfoapp', '0007_pensionmaster_color_hex'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetTypeMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_type_code', models.CharField(max_length=10)),
                ('asset_type_name', models.CharField(max_length=100)),
                ('color_hex', models.CharField(default='#264257', max_length=7)),
            ],
        ),
    ]
