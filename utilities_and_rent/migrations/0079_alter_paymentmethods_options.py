# Generated by Django 4.0.2 on 2022-03-15 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0078_remove_electricitymeter_for_building'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentmethods',
            options={'verbose_name_plural': 'Payment Options'},
        ),
    ]
