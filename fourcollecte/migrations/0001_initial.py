# Generated by Django 5.1.5 on 2025-02-16 17:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierCollecte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('WHOLESALER', 'Grossiste'), ('MANUFACTURER', 'Fabricant'), ('IMPORTER', 'Importateur'), ('LOCAL_DISTRIBUTOR', 'Distributeur local'), ('AGRICULTURAL_PRODUCER', 'Producteur agricole')], max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='suppliers/')),
                ('delivery_time', models.IntegerField(help_text='Délai de livraison moyen en jours')),
                ('order_frequency', models.CharField(help_text='Fréquence des commandes', max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SupplierContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField()),
                ('supplier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contact', to='fourcollecte.suppliercollecte')),
            ],
        ),
    ]
