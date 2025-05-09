# Generated by Django 4.2.7 on 2025-04-29 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0010_masterdropdowndata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actiondata',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_field_id', to='Form.formactionfield'),
        ),
        migrations.AlterField(
            model_name='actiondata',
            name='form_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_data_id', to='Form.formdata'),
        ),
        migrations.AlterField(
            model_name='fielddependency',
            name='dependent_on',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dependent_fields', to='Form.formfield'),
        ),
        migrations.AlterField(
            model_name='fielddependency',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dependencies', to='Form.formfield'),
        ),
        migrations.AlterField(
            model_name='fieldvalidation',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='validations', to='Form.formfield'),
        ),
        migrations.AlterField(
            model_name='fieldvalidation',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_validations', to='Form.form'),
        ),
        migrations.AlterField(
            model_name='fieldvalidation',
            name='sub_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='field_validations', to='Form.validationmaster'),
        ),
        migrations.AlterField(
            model_name='formactionfield',
            name='action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_action', to='Form.formaction'),
        ),
        migrations.AlterField(
            model_name='formdata',
            name='action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_action_id', to='Form.formaction'),
        ),
        migrations.AlterField(
            model_name='formdata',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_data_id', to='Form.form'),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fields', to='Form.form'),
        ),
        migrations.AlterField(
            model_name='formfieldvalues',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='field_value_id', to='Form.formfield'),
        ),
        migrations.AlterField(
            model_name='formfieldvalues',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_data', to='Form.form'),
        ),
        migrations.AlterField(
            model_name='formfieldvalues',
            name='form_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='form_value_id', to='Form.formdata'),
        ),
    ]
