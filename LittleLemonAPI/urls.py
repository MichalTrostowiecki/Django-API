from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<str:menuItem>/', views.SingleMenuItemView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # <-- This generates the token
    path('category/', views.CategoryView.as_view()),
]
