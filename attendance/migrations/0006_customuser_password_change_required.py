# Generated by Django 3.2.12 on 2024-05-06 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_worker_is_activated'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='password_change_required',
            field=models.BooleanField(default=False),
        ),
    ]
