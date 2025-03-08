# Generated by Django 5.1.5 on 2025-03-08 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_supplier_commune_supplier_quartier_supplier_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='latitude',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='longitude',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
