from django.db import models
from users.models import Client

class Wallet(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="wallets")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Balance: {self.balance}"
    
class Transfer(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="transfers")
    from_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transfers_sent")
    to_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transfers_received")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    transfer_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer {self.amount} from {self.from_wallet.name} to {self.to_wallet.name}"