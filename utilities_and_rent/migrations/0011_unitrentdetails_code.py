# Generated by Django 4.0.2 on 2022-02-26 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities_and_rent', '0010_alter_unitrentdetails_amount_paid_in_advance'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitrentdetails',
            name='code',
            field=models.CharField(blank=True, default='73892bgdv72R', max_length=15, null=True),
        ),
    ]