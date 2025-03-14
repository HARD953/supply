# Generated by Django 5.1.5 on 2025-03-15 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_date_creation_user_registre'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='commune',
            field=models.CharField(default='Abidjan', max_length=100, verbose_name='Commune'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='latitude',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='longitude',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='quartier',
            field=models.CharField(default='Rue15', max_length=100, verbose_name='Quartier'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='zone',
            field=models.CharField(default='ZoneB', max_length=100, verbose_name='Zone'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('WHOLESALER', 'Grossiste'), ('SEMI_WHOLESALER', 'Semi-grossiste'), ('RETAILER', 'Détaillant'), ('All', 'All')], max_length=20),
        ),
    ]
