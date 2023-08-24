# Generated by Django 4.2.3 on 2023-08-17 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Cancelled', 'cancelled'), ('Completed', 'Completed'), ('New', 'New')], default='New', max_length=10),
        ),
    ]
