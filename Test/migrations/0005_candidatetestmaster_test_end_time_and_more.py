# Generated by Django 4.2.7 on 2025-05-22 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Test', '0004_candidatetestmaster_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatetestmaster',
            name='test_end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='candidatetestmaster',
            name='test_start_time',
            field=models.DateTimeField(null=True),
        ),
    ]
