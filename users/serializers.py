from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client

class WalletBasicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class ClientWithWalletsSerializer(serializers.ModelSerializer):
    wallets = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'wallets']
    
    def get_wallets(self, obj):
        from wallets.models import Wallet
        wallets = Wallet.objects.filter(client=obj).values('id', 'name')
        return list(wallets)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Client.objects.create(
            name=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']  # DEV NOTE: Storing plain passwords is insecure
        )
        return user