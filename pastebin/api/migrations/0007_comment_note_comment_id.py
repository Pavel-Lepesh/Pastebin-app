# Generated by Django 4.2.7 on 2023-12-19 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='note_comment_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
