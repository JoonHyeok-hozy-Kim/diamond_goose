# Generated by Django 3.2.11 on 2022-02-22 12:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardapp', '0002_assethistory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('householdbookapp', '0006_buynowpaylater'),
    ]

    operations = [
        migrations.AddField(
            model_name='buynowpaylater',
            name='dashboard',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='buy_now_pay_later', to='dashboardapp.dashboard'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buynowpaylater',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='buy_now_pay_later', to='auth.user'),
            preserve_default=False,
        ),
    ]