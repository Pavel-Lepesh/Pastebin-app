# Generated by Django 4.2.7 on 2023-12-19 10:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0008_commentmetadata_comment_meta_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCommentRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(choices=[('LIKE', 'like'), ('DISLIKE', 'dislike')], max_length=7)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'comment')},
            },
        ),
    ]
