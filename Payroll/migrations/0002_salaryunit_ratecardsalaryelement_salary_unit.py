# Generated by Django 4.2.7 on 2025-05-23 06:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Payroll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salary_unit_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salary_unit_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'salary_unit',
            },
        ),
        migrations.AddField(
            model_name='ratecardsalaryelement',
            name='salary_unit',
            field=models.ForeignKey(blank=True, db_column='salary_unit', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rate_card_salary_unit', to='Payroll.salaryunit'),
        ),
    ]
