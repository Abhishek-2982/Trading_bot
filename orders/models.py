from django.db import models

class OrderResponse(models.Model):
    category = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
