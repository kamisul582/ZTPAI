# Generated by Django 3.2.12 on 2024-05-20 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_alter_customuser_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worktime',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
