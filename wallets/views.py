from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wallet
from .serializers import WalletSerializer
from users.models import Client

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = Client.objects.get(email=self.request.user.email)
            return Wallet.objects.filter(client=client)
        except Client.DoesNotExist:
            return Wallet.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(email=request.user.email)
            wallet = Wallet.objects.create(
                client=client,
                name=request.data.get('name'),
                balance=request.data.get('balance', 0.00)
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
        
        if instance.expenses.exists():
            return Response(
                {"error": "Cannot delete wallet with existing expenses"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get('amount', 0)
        try:
            amount = float(amount)
            wallet.balance += amount
            wallet.save()
            return Response({'balance': str(wallet.balance)})
        except ValueError:
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )