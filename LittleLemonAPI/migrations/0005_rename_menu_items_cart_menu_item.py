# Generated by Django 4.2.4 on 2023-08-20 15:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("LittleLemonAPI", "0004_remove_cart_items_cart_menu_items"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cart",
            old_name="menu_items",
            new_name="menu_item",
        ),
    ]