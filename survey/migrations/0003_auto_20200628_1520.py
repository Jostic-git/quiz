# Generated by Django 2.2.10 on 2020-06-28 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20200627_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='dateStart',
            field=models.DateTimeField(verbose_name='Дата старта'),
        ),
    ]
