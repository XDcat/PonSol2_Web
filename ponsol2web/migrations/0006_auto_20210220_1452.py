# Generated by Django 2.2.5 on 2021-02-20 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ponsol2web', '0005_auto_20210220_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='result',
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.TextField(null=True),
        ),
    ]
