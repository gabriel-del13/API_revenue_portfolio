from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal, InvalidOperation
from .models import Revenue
from .serializers import RevenueSerializer
from wallets.models import Wallet
from users.models import Client

class RevenueViewSet(viewsets.ModelViewSet):
    serializer_class = RevenueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Wallet.objects.none()
        try:
            client = Client.objects.get(email=self.request.user.email)
            queryset = Revenue.objects.filter(client=client, is_deleted=False)
            
            wallet_id = self.request.query_params.get('wallet_id', None)
            if wallet_id:
                queryset = queryset.filter(wallet_id=wallet_id)
            
            return queryset
        except Client.DoesNotExist:
            return Revenue.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(email=request.user.email)
            wallet_id = request.data.get('wallet')
            amount_str = request.data.get('amount')
            
            try:
                amount = Decimal(str(amount_str))
            except (ValueError, InvalidOperation):
                return Response(
                    {"error": "Invalid amount format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            wallet = Wallet.objects.get(id=wallet_id, client=client, is_deleted=False)
            
            revenue = Revenue.objects.create(
                client=client,
                wallet=wallet,
                name=request.data.get('name'),
                description=request.data.get('description'),
                amount=amount,
                revenue_date=request.data.get('revenue_date')
            )
            
            wallet.balance += amount
            wallet.save()
            
            serializer = self.get_serializer(revenue)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found or doesn't belong to you"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            if instance.client != client:
                return Response(
                    {"error": "You don't have permission to edit this revenue"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        old_amount = instance.amount
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        new_amount_str = serializer.validated_data.get('amount', old_amount)
        
        try:
            new_amount = Decimal(str(new_amount_str))
            if new_amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, InvalidOperation):
            return Response(
                {"error": "Invalid amount format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        difference = new_amount - old_amount
        
        wallet = instance.wallet
        wallet.balance += difference 
        wallet.save()
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            if instance.client != client:
                return Response(
                    {"error": "You don't have permission to delete this revenue"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        wallet = instance.wallet
        wallet.balance -= instance.amount
        wallet.save()
        
        instance.is_deleted = True
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)