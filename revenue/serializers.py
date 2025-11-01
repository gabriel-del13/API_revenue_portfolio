from rest_framework import serializers
from .models import Revenue

class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = ['id', 'wallet', 'name', 'description', 'amount', 'revenue_date']
        read_only_fields = ['id']