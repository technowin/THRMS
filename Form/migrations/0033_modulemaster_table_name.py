# Generated by Django 4.2.7 on 2025-06-10 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0032_form_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulemaster',
            name='table_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
