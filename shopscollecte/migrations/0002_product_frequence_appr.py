# Generated by Django 5.1.5 on 2025-02-19 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopscollecte', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='frequence_appr',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
