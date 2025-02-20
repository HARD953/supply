# Generated by Django 5.1.5 on 2025-02-16 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('MANUFACTURER', 'Fabricant'), ('DISTRIBUTOR', 'Distributeur'), ('WHOLESALER', 'Grossiste')], max_length=20)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField()),
                ('average_delivery_time', models.IntegerField()),
                ('order_frequency', models.CharField(max_length=100)),
            ],
        ),
    ]
