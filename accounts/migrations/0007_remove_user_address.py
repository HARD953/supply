# Generated by Django 5.1.5 on 2025-03-15 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_user_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
    ]
