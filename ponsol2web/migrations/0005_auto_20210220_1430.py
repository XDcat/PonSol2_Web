# Generated by Django 2.2.5 on 2021-02-20 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ponsol2web', '0004_auto_20210216_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='error_msg',
            field=models.TextField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='result',
            field=models.BooleanField(null=True),
        ),
    ]
