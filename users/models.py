from django.db import models

class Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
