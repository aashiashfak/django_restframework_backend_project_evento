# Generated by Django 5.0.3 on 2024-04-03 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_pendinguser_alter_customuser_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_superadmin',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
