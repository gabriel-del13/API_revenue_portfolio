from rest_framework import serializers
from .models import Wallet, Transfer

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'description', 'balance']
        read_only_fields = ['id']
        extra_kwargs = {
            'balance': {'required': False, 'read_only': True} 
        }
        
    def create(self, validated_data):
        balance = validated_data.pop('balance', 0.00)
        wallet = Wallet.objects.create(balance=balance, **validated_data)
        return wallet
    
class TransferSerializer(serializers.ModelSerializer):
    from_wallet_name = serializers.CharField(source='from_wallet.name', read_only=True)
    to_wallet_name = serializers.CharField(source='to_wallet.name', read_only=True)
    
    class Meta:
        model = Transfer
        fields = ['id', 'from_wallet', 'from_wallet_name', 'to_wallet', 'to_wallet_name', 
                  'amount', 'description', 'transfer_date']
        read_only_fields = ['id', 'transfer_date']