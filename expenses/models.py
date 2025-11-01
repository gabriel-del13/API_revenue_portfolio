from django.db import models
from users.models import Client
from wallets.models import Wallet

class Expense(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="expenses")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="expenses")
    name = models.CharField(max_length=100)
    description = models.TextField(null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()

    def __str__(self):
        return f"Expense: {self.description} - {self.amount}"
