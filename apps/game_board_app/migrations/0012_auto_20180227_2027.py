# Generated by Django 2.0.2 on 2018-02-27 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game_board_app', '0011_auto_20180227_1827'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='score',
            new_name='health',
        ),
    ]