# Generated by Django 4.0.2 on 2022-03-22 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental_property', '0015_alter_maintanancenotice_maintanance_status'),
        ('utilities', '0003_alter_payonlinempesa_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterbilling',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rental_property.building'),
        ),
    ]