# Generated by Django 5.0 on 2023-12-16 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('slug', models.CharField(max_length=200)),
                ('system_image_url', models.URLField(blank=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]