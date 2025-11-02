from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models  # AGREGAR ESTE IMPORT
from decimal import Decimal, InvalidOperation
from .models import Wallet, Transfer
from .serializers import WalletSerializer, TransferSerializer
from users.models import Client

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = Client.objects.get(email=self.request.user.email)
            return Wallet.objects.filter(client=client, is_deleted=False)
        except Client.DoesNotExist:
            return Wallet.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(email=request.user.email)
            
            balance = request.data.get('balance', 0.00)
            try:
                balance = Decimal(str(balance))
                if balance < 0:
                    return Response(
                        {"error": "Balance cannot be negative"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, InvalidOperation):
                return Response(
                    {"error": "Invalid balance amount"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            wallet = Wallet.objects.create(
                client=client,
                name=request.data.get('name'),
                description=request.data.get('description'),
                balance=balance
            )
            serializer = self.get_serializer(wallet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            if instance.client != client:
                return Response(
                    {"error": "You don't have permission to edit this wallet"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            if instance.client != client:
                return Response(
                    {"error": "You don't have permission to delete this wallet"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        instance.is_deleted = True 
        instance.save() 

        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get('amount', 0)
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response(
                    {'error': 'Amount must be positive'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            wallet.balance += amount
            wallet.save()
            serializer = self.get_serializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, InvalidOperation):
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transferir dinero de esta wallet a otra wallet del mismo usuario"""
        from_wallet = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            
            if from_wallet.client != client:
                return Response(
                    {"error": "You don't have permission to transfer from this wallet"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            to_wallet_id = request.data.get('to_wallet')
            amount_str = request.data.get('amount')
            description = request.data.get('description', '')
            
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
            
            to_wallet = Wallet.objects.get(id=to_wallet_id, client=client, is_deleted=False)
            
            if from_wallet.id == to_wallet.id:
                return Response(
                    {"error": "Cannot transfer to the same wallet"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if from_wallet.balance < amount:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from_wallet.balance -= amount
            to_wallet.balance += amount
            from_wallet.save()
            to_wallet.save()
            
            transfer = Transfer.objects.create(
                client=client,
                from_wallet=from_wallet,
                to_wallet=to_wallet,
                amount=amount,
                description=description
            )
            
            serializer = TransferSerializer(transfer)
            return Response({
                'message': 'Transfer successful',
                'transfer': serializer.data,
                'from_wallet_balance': str(from_wallet.balance),
                'to_wallet_balance': str(to_wallet.balance)
            }, status=status.HTTP_201_CREATED)
            
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Destination wallet not found or doesn't belong to you"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def transfers(self, request):
        """Ver historial de todas las transferencias del usuario"""
        try:
            client = Client.objects.get(email=request.user.email)
            transfers = Transfer.objects.filter(client=client).order_by('-transfer_date')
            
            # Filtrar por wallet específica si se proporciona
            wallet_id = request.query_params.get('wallet_id', None)
            if wallet_id:
                transfers = transfers.filter(
                    models.Q(from_wallet_id=wallet_id) | models.Q(to_wallet_id=wallet_id)
                )
            
            serializer = TransferSerializer(transfers, many=True)
            return Response(serializer.data)
            
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )