# Generated by Django 4.0.4 on 2022-06-20 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boxes', '0010_storage_lat_storage_lng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='lng',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
    ]
