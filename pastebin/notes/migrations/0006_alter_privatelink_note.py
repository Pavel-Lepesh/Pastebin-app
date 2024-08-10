# Generated by Django 4.2.7 on 2024-06-19 13:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0005_privatelink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatelink',
            name='note',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.note', unique=True),
        ),
    ]
