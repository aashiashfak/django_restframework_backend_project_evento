# Generated by Django 5.0.3 on 2024-04-04 11:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_customuser_is_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='auth_provider',
        ),
    ]
