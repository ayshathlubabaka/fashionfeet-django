# Generated by Django 4.2.3 on 2023-08-09 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_order_status_alter_orderproduct_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('New', 'New'), ('Completed', 'Completed'), ('Cancelled', 'cancelled')], default='New', max_length=10),
        ),
    ]
