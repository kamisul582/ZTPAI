# Generated by Django 4.2.6 on 2024-03-20 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_workers', to='attendance.worker'),
        ),
        migrations.DeleteModel(
            name='Manager',
        ),
    ]
