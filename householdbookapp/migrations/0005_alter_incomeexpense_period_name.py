# Generated by Django 3.2.11 on 2022-02-13 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('householdbookapp', '0004_incomeexpense'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomeexpense',
            name='period_name',
            field=models.CharField(max_length=10),
        ),
    ]
