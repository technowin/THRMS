# Generated by Django 4.2.7 on 2025-05-22 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Test', '0003_candidateanswer_candidate_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatetestmaster',
            name='percentage',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='candidatetestmaster',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='candidatetestmaster',
            name='time_taken',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
