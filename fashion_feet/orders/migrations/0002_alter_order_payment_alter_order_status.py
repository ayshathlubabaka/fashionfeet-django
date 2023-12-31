# Generated by Django 4.2.3 on 2023-08-08 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.payment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Cancelled', 'cancelled'), ('New', 'New'), ('Completed', 'Completed'), ('Accepted', 'Accepted')], default='New', max_length=10),
        ),
    ]
