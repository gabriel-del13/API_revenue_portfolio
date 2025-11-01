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
        
        wallet_name = str(instance) 
        
        force_delete = request.query_params.get('force', '').lower() in ['true', '1']
        if force_delete:
            instance.expenses.all().delete()
            confirmation_message = f"Wallet '{wallet_name}' and all associated expenses were successfully deleted."
        else:
            confirmation_message = f"Wallet '{wallet_name}' was successfully deleted."

        self.perform_destroy(instance)
        
        return Response(
            {"message": confirmation_message}, 
            status=status.HTTP_200_OK 
        )
        
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