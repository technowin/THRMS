# Generated by Django 4.2.7 on 2025-07-07 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0018_remove_citymaster_city_status'),
        ('attendance', '0024_alter_attendancelog_in_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyattendance',
            name='a',
        ),
        migrations.RemoveField(
            model_name='dailyattendance',
            name='p',
        ),
        migrations.AddField(
            model_name='dailyattendance',
            name='company_id',
            field=models.ForeignKey(db_column='company_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comapny_att_id', to='Masters.company_master'),
        ),
        migrations.AddField(
            model_name='dailyattendance',
            name='is_present',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dailyattendance',
            name='site_id',
            field=models.ForeignKey(db_column='site_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='site_att_id', to='Masters.site_master'),
        ),
        migrations.AlterField(
            model_name='dailyattendance',
            name='cl',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailyattendance',
            name='other_leave',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailyattendance',
            name='pl',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailyattendance',
            name='sl',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
