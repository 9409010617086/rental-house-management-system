# Generated by Django 4.0.2 on 2022-03-08 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0071_alter_electricitybilling_units'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electricitybilling',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=9, null=True),
        ),
    ]