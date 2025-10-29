from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Expense
from .serializers import ExpenseSerializer
from wallets.models import Wallet

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        client_id = serializer.validated_data['client'].id
        amount = serializer.validated_data['amount']
        
        # Buscar wallet del cliente
        try:
            wallet = Wallet.objects.get(client_id=client_id)
            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Insufficient balance in wallet'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Client does not have a wallet'}, 
                status=status.HTTP_400_BAD_REQUEST
            )