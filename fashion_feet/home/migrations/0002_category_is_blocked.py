# Generated by Django 4.2.3 on 2023-08-09 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]