# Generated by Django 3.2.9 on 2022-01-21 14:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sinha', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='date_time_of_payment',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 1, 21, 2, 28, 12, 969410), null=True, verbose_name='date time of payment'),
        ),
    ]
