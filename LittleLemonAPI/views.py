from django.shortcuts import render
from rest_framework import generics, status
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404


class MenuItemView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request):
        item = MenuItem.objects.all()
        serializer = MenuItemSerializer(item, many=True)
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
def managers(request):
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
@permission_classes([IsAdminUser])
def deleteManager(request, userId):

    user = get_object_or_404(User, id=userId)

    if request.method == 'DELETE':
        managers_group = Group.objects.get(name='Manager')
        if user in managers_group.user_set.all():
            managers_group.user_set.remove(user)
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