# Generated by Django 4.2.7 on 2025-07-01 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0014_timecorrection'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarlyLeaveApply',
            fields=[
                ('early_leave_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('employee_id', models.BigIntegerField(blank=True, null=True)),
                ('leave_date', models.DateField(blank=True, default=None, null=True)),
                ('leave_time', models.TimeField(blank=True, default=None, null=True)),
                ('reason_for_leave', models.CharField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'early_leave_application',
            },
        ),
        migrations.CreateModel(
            name='LeaveApply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.BigIntegerField(blank=True, null=True)),
                ('from_date', models.DateField(blank=True, default=None, null=True)),
                ('to_date', models.DateField(blank=True, default=None, null=True)),
                ('leave_id', models.CharField(blank=True, max_length=255, null=True)),
                ('reason_for_leave', models.CharField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('leave_status_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'leave_application_details',
            },
        ),
    ]
