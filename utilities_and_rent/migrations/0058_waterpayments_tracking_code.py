# Generated by Django 4.0.2 on 2022-03-07 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0057_electricitypayments_lock'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterpayments',
            name='tracking_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]