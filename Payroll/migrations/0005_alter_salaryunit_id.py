# Generated by Django 4.2.7 on 2025-05-23 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payroll', '0004_rename_value_salaryunit_unit_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salaryunit',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
