# Generated by Django 5.0 on 2024-01-29 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_sub_topics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsubtopic',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='eventsubtopic',
            name='slug',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]