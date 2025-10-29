from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Client
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    @action(detail=True, methods=['get'])
    def wallets(self, request, pk=None):
        client = self.get_object()
        from wallets.serializers import WalletSerializer
        wallets = client.wallets.all()
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        client = self.get_object()
        from expenses.serializers import ExpenseSerializer
        expenses = client.expenses.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)