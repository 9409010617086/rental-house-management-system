# Generated by Django 4.0.2 on 2022-03-22 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_property', '0014_remove_maintanancenotice_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintanancenotice',
            name='maintanance_status',
            field=models.CharField(choices=[('Not Started', 'Not Yet Started'), ('In Progress', 'In progress'), ('Completed', 'Completed')], default='Not Started', max_length=20),
        ),
    ]