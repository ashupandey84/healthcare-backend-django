from django.conf import settings
from django.db import models
class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["name", "id"]
    def __str__(self): return f"{self.name} ({self.specialization})"
