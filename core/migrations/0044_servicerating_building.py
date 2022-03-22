# Generated by Django 4.0.2 on 2022-03-22 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental_property', '0011_alter_rentalunit_options'),
        ('core', '0043_alter_contact_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerating',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rental_property.building'),
        ),
    ]