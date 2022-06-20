# Generated by Django 4.0.4 on 2022-06-16 02:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("boxes", "0004_box_is_occupied"),
    ]

    operations = [
        migrations.CreateModel(
            name="CalcRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        db_index=True, max_length=100, verbose_name="Email"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="Дата создания",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("NEW", "новый"), ("PRC", "обработан")],
                        db_index=True,
                        default="NEW",
                        max_length=3,
                        verbose_name="Cтатус",
                    ),
                ),
            ],
            options={
                "verbose_name": "запрос на рассчет",
                "verbose_name_plural": "запросы на рассчет",
            },
        ),
    ]
