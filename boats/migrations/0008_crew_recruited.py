# Generated by Django 2.0.3 on 2018-04-27 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0007_auto_20180425_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='crew',
            name='recruited',
            field=models.BooleanField(default=False),
        ),
    ]
