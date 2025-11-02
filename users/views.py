from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import Client
from .serializers import UserRegistrationSerializer, ClientWithWalletsSerializer
from expenses.models import Expense
from revenue.models import Revenue
from wallets.models import Wallet


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
        serializer = ClientWithWalletsSerializer(client)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Dashboard con estadísticas financieras del usuario"""
    try:
        client = Client.objects.get(email=request.user.email)
        
        # Parámetros opcionales
        year = request.query_params.get('year', datetime.now().year)
        month = request.query_params.get('month', None)
        
        # Filtros base
        expenses_qs = Expense.objects.filter(client=client)
        revenues_qs = Revenue.objects.filter(client=client)
        
        # Filtrar por año
        expenses_qs = expenses_qs.filter(expense_date__year=year)
        revenues_qs = revenues_qs.filter(revenue_date__year=year)
        
        # Si se especifica mes, filtrar
        if month:
            expenses_qs = expenses_qs.filter(expense_date__month=month)
            revenues_qs = revenues_qs.filter(revenue_date__month=month)
        
        # Totales generales
        total_expenses = expenses_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_revenues = revenues_qs.aggregate(total=Sum('amount'))['total'] or 0
        balance = total_revenues - total_expenses
        
        # Totales por mes
        expenses_by_month = (
            Expense.objects.filter(client=client, expense_date__year=year)
            .annotate(month=TruncMonth('expense_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        
        revenues_by_month = (
            Revenue.objects.filter(client=client, revenue_date__year=year)
            .annotate(month=TruncMonth('revenue_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        
        # Balance por wallet
        wallets = Wallet.objects.filter(client=client)
        wallets_summary = [{
            'id': w.id,
            'name': w.name,
            'balance': str(w.balance)
        } for w in wallets]
        
        # Balance histórico (últimos 6 meses)
        six_months_ago = datetime.now() - timedelta(days=180)
        historical_balance = []
        
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            
            month_revenues = Revenue.objects.filter(
                client=client,
                revenue_date__lte=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expenses = Expense.objects.filter(
                client=client,
                expense_date__lte=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            historical_balance.insert(0, {
                'month': month_start.strftime('%Y-%m'),
                'balance': float(month_revenues - month_expenses)
            })
        
        # Top 5 gastos más grandes
        top_expenses = expenses_qs.order_by('-amount')[:5].values(
            'id', 'name', 'amount', 'expense_date'
        )
        
        # Top 5 ingresos más grandes
        top_revenues = revenues_qs.order_by('-amount')[:5].values(
            'id', 'name', 'amount', 'revenue_date'
        )
        
        data = {
            'summary': {
                'total_revenues': str(total_revenues),
                'total_expenses': str(total_expenses),
                'balance': str(balance),
                'period': f"{year}" + (f"-{month}" if month else "")
            },
            'monthly_comparison': {
                'expenses': [
                    {
                        'month': item['month'].strftime('%Y-%m'),
                        'total': str(item['total'])
                    } for item in expenses_by_month
                ],
                'revenues': [
                    {
                        'month': item['month'].strftime('%Y-%m'),
                        'total': str(item['total'])
                    } for item in revenues_by_month
                ]
            },
            'wallets_summary': wallets_summary,
            'historical_balance': historical_balance,
            'top_expenses': list(top_expenses),
            'top_revenues': list(top_revenues)
        }
        
        return Response(data)
        
    except Client.DoesNotExist:
        return Response(
            {"error": "Client profile not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )