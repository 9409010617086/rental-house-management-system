# Generated by Django 4.0.2 on 2022-03-11 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_order', '0010_alter_workorder_additional_workers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorder',
            name='email_personnel',
            field=models.BooleanField(default=False),
        ),
    ]