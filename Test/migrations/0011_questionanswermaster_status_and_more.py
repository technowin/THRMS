# Generated by Django 4.2.7 on 2025-06-02 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Test', '0010_temporaryquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswermaster',
            name='status',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='candidatetestmaster',
            name='status',
            field=models.IntegerField(null=True),
        ),
    ]
