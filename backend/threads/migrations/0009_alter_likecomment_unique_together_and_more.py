# Generated by Django 5.2.2 on 2025-06-20 02:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0008_comment_app_comment_repost__932f99_idx_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='likecomment',
            unique_together={('user', 'comment')},
        ),
        migrations.AlterUniqueTogether(
            name='likepost',
            unique_together={('user', 'post')},
        ),
    ]
