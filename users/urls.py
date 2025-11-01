from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    register, 
    my_profile, 
    list_all_users, 
    delete_user, 
    change_user_password
)

urlpatterns = [
    # Públicas
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuario autenticado
    path('me/', my_profile, name='my_profile'),
    
    # Admin only
    path('admin/', list_all_users, name='list_all_users'),
    path('admin/<int:user_id>/', delete_user, name='delete_user'),
    path('admin/<int:user_id>/change-password/', change_user_password, name='change_user_password'),
]
