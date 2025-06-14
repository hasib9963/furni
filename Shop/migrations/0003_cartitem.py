# Generated by Django 5.2 on 2025-05-04 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Shop', '0002_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Shop.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Shop.product')),
            ],
        ),
    ]
