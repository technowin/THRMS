# Generated by Django 4.2.7 on 2025-06-06 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0022_alter_formfield_foriegn_key_form_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='foriegn_key_form_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
