# Generated by Django 4.0.2 on 2022-03-15 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0015_unitreport_other'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitreport',
            name='desc',
            field=models.TextField(verbose_name='Describe the situation'),
        ),
    ]