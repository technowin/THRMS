# Generated by Django 4.2.7 on 2025-06-17 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Workflow', '0013_rec_history_workflow_details_candidate_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rec_history_workflow_details',
            name='operator',
        ),
        migrations.AddField(
            model_name='rec_workflow_details',
            name='increment_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
