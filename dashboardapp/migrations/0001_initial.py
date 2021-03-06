# Generated by Django 3.2.11 on 2022-01-30 14:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('masterinfoapp', '0002_alter_assetmaster_asset_type'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='dashboard', serialize=False, to='auth.user')),
                ('initial_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
                ('main_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='main_currency', to='masterinfoapp.currencymaster')),
            ],
        ),
    ]
