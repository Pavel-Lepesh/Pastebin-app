# Generated by Django 4.2.7 on 2023-12-19 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_comment_note_comment_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentMetaData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='meta_data',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.commentmetadata'),
            preserve_default=False,
        ),
    ]
