# Generated by Django 5.1.3 on 2024-11-08 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game_Territory', '0004_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
