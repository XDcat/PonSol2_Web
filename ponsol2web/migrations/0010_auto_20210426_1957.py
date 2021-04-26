# Generated by Django 3.1.5 on 2021-04-26 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ponsol2web', '0009_auto_20210414_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='email_res',
            field=models.TextField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='input_type',
            field=models.TextField(choices=[('id', 'ID'), ('seq', 'Sequence'), ('protein', 'Protein')], max_length=10, null=True),
        ),
    ]
