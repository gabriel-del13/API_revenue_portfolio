from rest_framework import serializers
from .models import Revenue

class RevenueSerializer(serializers.ModelSerializer):
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    
    class Meta:
        model = Revenue
        fields = ['id', 'wallet', 'wallet_name', 'name', 'description', 'amount', 'revenue_date']
        read_only_fields = ['id']