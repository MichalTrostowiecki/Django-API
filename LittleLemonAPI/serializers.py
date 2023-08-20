from .models import Category, MenuItem, Cart, CartItem, Order
from rest_framework import serializers
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'title', 'price', 'category', 'featured')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'groups')


class CartSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='cart.user.username')
    menu_item_name = serializers.ReadOnlyField(source='menu_item.title')

    class Meta:
        model = CartItem
        fields = ('cart', 'user_username', 'menu_item_name', 'menu_item', 'quantity')


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('cart', 'menu_item', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'