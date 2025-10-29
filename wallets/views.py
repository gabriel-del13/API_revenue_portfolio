from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet
from .serializers import WalletSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    
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
    
    @action(detail=True, methods=['post'])
    def subtract_balance(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get('amount', 0)
        try:
            amount = float(amount)
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()
                return Response({'balance': str(wallet.balance)})
            else:
                return Response(
                    {'error': 'Insufficient balance'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )