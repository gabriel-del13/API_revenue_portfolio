from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'wallet', 'wallet_name', 'name', 'description', 'amount', 'expense_date']
        read_only_fields = ['id']