from django.conf import settings
from django.db import models
class Patient(models.Model):
    GENDERS = [("female","Female"),("male","Male"),("other","Other"),("prefer_not_to_say","Prefer not to say")]
    name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDERS)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patients")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.name
