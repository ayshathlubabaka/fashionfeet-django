# Generated by Django 4.2.3 on 2023-08-12 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Cancelled', 'cancelled'), ('Completed', 'Completed'), ('New', 'New')], default='New', max_length=10),
        ),
    ]
