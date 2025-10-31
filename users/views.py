from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Client
from .serializers import UserRegistrationSerializer, ClientSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User created successfully"}, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    try:
        client = Client.objects.get(email=request.user.email)
        serializer = ClientSerializer(client)
        return Response(serializer.data)
    except Client.DoesNotExist:
        return Response(
            {"error": "Client profile not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

# ADMIN ENDPOINTS
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_all_users(request):
    """Solo admin puede ver todos los usuarios"""
    users = User.objects.all()
    data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined
    } for user in users]
    return Response(data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    """Solo admin puede eliminar usuarios"""
    try:
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            return Response(
                {"error": "Cannot delete superuser"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
def change_user_password(request, user_id):
    """Solo admin puede cambiar contraseñas"""
    try:
        user = User.objects.get(id=user_id)
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {"error": "new_password is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )