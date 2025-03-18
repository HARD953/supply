# Generated by Django 5.1.5 on 2025-03-18 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='commune',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Commune'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_creation',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='accounts_users/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='quartier',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Quartier'),
        ),
        migrations.AlterField(
            model_name='user',
            name='registre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='zone',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
