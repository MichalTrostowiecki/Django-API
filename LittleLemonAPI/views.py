from django.shortcuts import render
from rest_framework import generics, status
from .models import MenuItem, Category, Cart, CartItem, Order
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartItemSerializer, CartSerializer, OrderSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django_filters.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class MenuItemView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    search_fields = ['title']

    def get(self, request):
        items = self.filter_queryset(self.get_queryset())
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, 200)

    def post(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'message': "Only managers can create items."}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'title'
    lookup_url_kwarg = 'menuItem'

    def get(self, request, *args, **kwargs):
        try:
            title_with_hyphens = self.kwargs['menuItem']
            title = title_with_hyphens.replace('-', ' ')
            item = MenuItem.objects.get(title=title)
            serializer = MenuItemSerializer(item)

            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'message': "Item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'Only Managers can update items'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'Only Manager can delete items'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().delete(request, *args, **kwargs)
  
    def patch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'Only Manager can update items'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().patch(request, *args, **kwargs)


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def managersView(request):
    if request.method == 'POST':
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message': 'User added to the manager group'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Username is required for adding user to the manager group'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        managers_group = Group.objects.get(name='Manager')
        managers = managers_group.user_set.all()
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)

    return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def deleteManagerView(request, userId):

    user = get_object_or_404(User, id=userId)

    if request.method == 'DELETE':
        managers_group = Group.objects.get(name='Manager')
        if user in managers_group.user_set.all():
            managers_group.user_set.remove(user)
            return Response({'message': 'Manager has been deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'GET':
        if user.groups.filter(name='Manager').exists():
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'message': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

   
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def deliveryCrewView(request):
    if request.method == 'GET':
        deliveryCrew_group = Group.objects.get(name='Delivery crew')
        deliveryCrew = deliveryCrew_group.user_set.all()
        serializer = UserSerializer(deliveryCrew, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'Only managers can add users to the delivery crew group'}, status=status.HTTP_403_FORBIDDEN)
        else:
            username = request.data.get('username')
            if username:
                user = get_object_or_404(User, username=username)
                deliveryCrew = Group.objects.get(name='Delivery crew')
                deliveryCrew.user_set.add(user)
                return Response({'message': 'user added to delivery crew group'}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def deleteDeliveryCrewView(request, userId):

    user = get_object_or_404(User, id=userId)

    if request.method == 'DELETE':
        deliveryCrew_groups = Group.objects.get(name='Delivery crew')
        if user in deliveryCrew_groups.user_set.all():
            deliveryCrew_groups.user_set.remove(user)
            return Response({'message': 'user removed from the delivery crew'}, status=status.HTTP_200_OK)
    elif request.method == 'GET':
        if user.groups.filter(name='Delivery crew').exists():
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    if request.method == 'GET':
        products = MenuItem.objects.filter(featured=False)  # You can adjust the filter as needed
        serializer = MenuItemSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        user = request.user
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 1)

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        cart_item.quantity += int(quantity)
        cart_item.save()
        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    serializer = CartSerializer(cart_items, many=True)# Use CartSerializer
    if request.method == 'DELETE':
        cart_items.delete()
        return Response({'message': 'Cart has been cleared'})
    else:
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)

    order = Order.objects.create(user=user)
    for cart_item in cart_items:
        order.items.add(cart_item.menu_item)

    return Response({'message': 'Order placed succesfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_orders(request):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'Only managers can view all orders'}, status=status.HTTP_403_FORBIDDEN)
    else:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_user_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def assign_orders(request):
    if request.method == 'GET':
        if not request.user.groups.filter(name='Delivery crew').exists() and not request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'Only delivery crew can view their orders'}, status=status.HTTP_403_FORBIDDEN)
        else:
            orders = Order.objects.filter(delivery_crew=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
    if request.method == 'POST':
        order_id = request.data.get('order_id')
        delivered = request.data.get('delivered', False)

        try:
            order = Order.objects.get(id=order_id)
            if request.user.groups.filter(name='Manager').exists():
                username = request.data.get('username')
                try:
                    delivery_crew = User.objects.get(username=username, groups__name='Delivery crew')
                    order.delivery_crew = delivery_crew
                    order.save()
                    return Response({'message': 'Order assigned to delivery crew member'}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'message': 'Delivery crew member not found'}, status=status.HTTP_404_NOT_FOUND)
            elif order.delivery_crew == request.user:
                order.delivered = delivered
                order.save()
                return Response({'message': 'Order status updated'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

