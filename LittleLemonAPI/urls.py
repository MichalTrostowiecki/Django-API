from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/menu-items/', views.MenuItemView.as_view()),
    path('api/menu-items/<str:menuItem>/', views.SingleMenuItemView.as_view()),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # <-- This generates the token
    path('category/', views.CategoryView.as_view()),
    path('api/groups/manager/users', views.managers),
    path('api/groups/manager/<int:userId>/', views.deleteManager),
    
]
