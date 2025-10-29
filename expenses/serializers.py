from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'client', 'description', 'amount', 'expense_date']
        read_only_fields = ['id']