# Generated by Django 5.1.3 on 2024-12-26 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_accessattempt'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AccessAttempt',
        ),
        migrations.DeleteModel(
            name='LoginAttempt',
        ),
    ]
