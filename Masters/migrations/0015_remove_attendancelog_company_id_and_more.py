# Generated by Django 4.2.7 on 2025-06-24 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0014_employeeshiftmapping_shiftmaster_attendancelog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendancelog',
            name='company_id',
        ),
        migrations.DeleteModel(
            name='EmployeeShiftMapping',
        ),
        migrations.RemoveField(
            model_name='shiftmaster',
            name='company_id',
        ),
        migrations.RemoveField(
            model_name='shiftmaster',
            name='site_id',
        ),
        migrations.DeleteModel(
            name='AttendanceLog',
        ),
        migrations.DeleteModel(
            name='ShiftMaster',
        ),
    ]
