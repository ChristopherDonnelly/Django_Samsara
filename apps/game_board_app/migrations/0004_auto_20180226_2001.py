# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-26 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_board_app', '0003_auto_20180226_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='square',
            name='status',
            field=models.CharField(default='None', max_length=255),
        ),
    ]
