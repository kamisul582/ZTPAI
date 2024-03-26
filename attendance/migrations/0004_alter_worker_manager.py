# Generated by Django 4.2.6 on 2024-03-20 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_alter_worker_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinate', to='attendance.worker'),
        ),
    ]