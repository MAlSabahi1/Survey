# Generated by Django 5.1.3 on 2024-12-15 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_alter_question_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.CharField(max_length=200),
        ),
    ]
