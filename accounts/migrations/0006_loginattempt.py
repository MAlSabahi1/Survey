# Generated by Django 5.1.3 on 2024-12-30 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_actionlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('username', models.CharField(blank=True, max_length=150, null=True)),
                ('attempt_time', models.DateTimeField(auto_now_add=True)),
                ('failures_since_start', models.IntegerField(default=0)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('browser', models.CharField(blank=True, max_length=100, null=True)),
                ('os', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
