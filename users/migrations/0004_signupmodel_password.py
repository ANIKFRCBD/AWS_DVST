# Generated by Django 4.2.2 on 2023-10-17 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_signupmodel_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='signupmodel',
            name='password',
            field=models.CharField(default='my_default_password', max_length=128),
        ),
    ]
