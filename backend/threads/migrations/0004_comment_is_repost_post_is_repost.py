# Generated by Django 5.2.2 on 2025-06-10 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0003_user_is_repost_post_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_repost',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='is_repost',
            field=models.BooleanField(default=False),
        ),
    ]
