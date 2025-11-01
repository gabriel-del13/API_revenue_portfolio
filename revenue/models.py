from django.db import models
from users.models import Client
from wallets.models import Wallet

class Revenue(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="revenues")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="revenues")
    name = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    revenue_date = models.DateField()

    def __str__(self):
        return f"{self.name}: {self.description} - {self.amount}"