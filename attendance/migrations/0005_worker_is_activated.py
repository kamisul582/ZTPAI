# Generated by Django 4.2.6 on 2024-03-23 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_alter_worker_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='is_activated',
            field=models.BooleanField(default=False),
        ),
    ]
