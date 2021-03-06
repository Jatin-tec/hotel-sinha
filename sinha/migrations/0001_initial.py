# Generated by Django 3.2.9 on 2022-01-18 12:56

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='sinha', max_length=30)),
                ('owner', models.CharField(max_length=20)),
                ('location', models.CharField(default='chhindwara', max_length=50)),
                ('state', models.CharField(default='madhya pradesh', max_length=50)),
                ('country', models.CharField(default='india', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.IntegerField()),
                ('item_name', models.CharField(max_length=50)),
                ('item_total', models.IntegerField()),
                ('item_available', models.IntegerField()),
                ('item_not_available', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Rooms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_type', models.CharField(choices=[('1', 'premium'), ('2', 'deluxe'), ('3', 'basic')], max_length=50)),
                ('capacity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('size', models.IntegerField()),
                ('status', models.CharField(choices=[('1', 'available'), ('2', 'not available')], max_length=15)),
                ('roomnumber', models.IntegerField()),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sinha.hotels')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('total_amount', models.CharField(blank=True, max_length=100, null=True, verbose_name='total amount')),
                ('payment_status', models.CharField(choices=[('1', 'PENDING'), ('2', 'SUCCESS')], default=None, max_length=10, null=True, verbose_name='payment sucess')),
                ('date_time_of_payment', models.DateTimeField(blank=True, default=datetime.datetime(2022, 1, 18, 0, 56, 1, 68636), null=True, verbose_name='date time of payment')),
                ('razorpay_order_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='Razorpay order id')),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='Razorpay payment id')),
                ('razorpay_signature_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='Razorpay signature')),
                ('booking_id', models.CharField(default='null', max_length=100)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sinha.rooms')),
            ],
        ),
    ]
