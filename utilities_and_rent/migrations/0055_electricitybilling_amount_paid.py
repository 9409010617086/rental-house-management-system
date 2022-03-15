# Generated by Django 4.0.2 on 2022-03-07 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0054_electricitypayments_payment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='electricitybilling',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
    ]