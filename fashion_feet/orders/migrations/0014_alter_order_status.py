# Generated by Django 4.2.3 on 2023-08-13 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Completed', 'Completed'), ('New', 'New'), ('Cancelled', 'cancelled')], default='New', max_length=10),
        ),
    ]
