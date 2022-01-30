# Generated by Django 3.2.11 on 2022-01-30 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assetapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assettransaction',
            name='asset',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='assetapp.asset'),
            preserve_default=False,
        ),
    ]
