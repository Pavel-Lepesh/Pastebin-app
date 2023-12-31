# Generated by Django 4.2.7 on 2023-12-13 10:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteMetaData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('views', models.IntegerField(default=0)),
                ('stars', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('hash_link', models.CharField(db_index=True, max_length=200, unique=True)),
                ('time_create', models.DateTimeField(auto_now_add=True)),
                ('time_update', models.DateTimeField(auto_now=True)),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('key_for_s3', models.UUIDField()),
                ('meta_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.notemetadata')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='username')),
            ],
        ),
    ]
