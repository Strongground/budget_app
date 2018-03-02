# Generated by Django 2.0.1 on 2018-02-01 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0004_transaction_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('in', 'EARNING'), ('out', 'SPENDING')], max_length=50),
        ),
    ]
