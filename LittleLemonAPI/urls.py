from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/menu-items/', views.MenuItemView.as_view()),
    path('api/menu-items/<str:menuItem>/', views.SingleMenuItemView.as_view()),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('category/', views.CategoryView.as_view()),
    path('api/groups/manager/users', views.managersView),
    path('api/groups/manager/users/<int:userId>/', views.deleteManagerView),
    path('api/groups/delivery-crew/users', views.deliveryCrewView),
    path('api/groups/delivery-crew/users/<int:userId>', views.deleteDeliveryCrewView),
    path('api/cart', views.view_cart),
    path('api/add-to-cart', views.add_to_cart),
    path('api/place-order', views.place_order),
    path('api/view-orders', views.view_all_orders),
    path('api/view-my-order', views.view_user_orders),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/assign-orders', views.assign_orders),
]
