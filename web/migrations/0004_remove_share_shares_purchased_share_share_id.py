# Generated by Django 4.1.7 on 2023-07-11 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_share_outstanding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='share',
            name='shares_purchased',
        ),
        migrations.AddField(
            model_name='share',
            name='share_id',
            field=models.UUIDField(auto_created=True, default=0),
            preserve_default=False,
        ),
    ]
