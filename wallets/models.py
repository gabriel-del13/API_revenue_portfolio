from django.db import models
from users.models import Client

class Wallet(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="wallets")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet {self.id} - Balance: {self.balance}"
