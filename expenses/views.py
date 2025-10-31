from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializers import ExpenseSerializer
from wallets.models import Wallet
from users.models import Client

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = Client.objects.get(email=self.request.user.email)
            queryset = Expense.objects.filter(client=client)
            wallet_id = self.request.query_params.get('wallet_id', None)
            if wallet_id:
                queryset = queryset.filter(wallet_id=wallet_id)
            
            return queryset
        except Client.DoesNotExist:
            return Expense.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(email=request.user.email)
            wallet_id = request.data.get('wallet')
            amount = float(request.data.get('amount'))
            
            wallet = Wallet.objects.get(id=wallet_id, client=client)
            
            if wallet.balance >= amount:
                expense = Expense.objects.create(
                    client=client,
                    wallet=wallet,
                    name=request.data.get('name'),
                    description=request.data.get('description'),
                    amount=amount,
                    expense_date=request.data.get('expense_date')
                )
                
                wallet.balance -= amount
                wallet.save()
                
                serializer = self.get_serializer(expense)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Insufficient balance'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
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
                    {"error": "You don't have permission to edit this expense"},
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
        
        new_amount = serializer.validated_data.get('amount', old_amount)
        difference = new_amount - old_amount
        
        wallet = instance.wallet
        if wallet.balance >= difference:
            wallet.balance -= difference
            wallet.save()
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Insufficient balance for this update'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        try:
            client = Client.objects.get(email=request.user.email)
            if instance.client != client:
                return Response(
                    {"error": "You don't have permission to delete this expense"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        wallet = instance.wallet
        wallet.balance += instance.amount
        wallet.save()
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)