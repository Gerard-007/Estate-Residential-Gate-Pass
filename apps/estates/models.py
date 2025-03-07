from django.db import models
from django.conf import settings
import uuid
from apps.authentication.models import User


class Estate(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    estate_manager = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estate_manager')

    class Meta:
        unique_together = ('name', 'address')

    def __str__(self):
        return f"{self.name} - {self.city}"


class Apartment(models.Model):
    name = models.CharField(max_length=100)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    resident = models.OneToOneField(User, related_name='apartment', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'estate')

    def __str__(self):
        return f"{self.estate} - {self.name}"


class VisitorToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    visitor_name = models.CharField(max_length=255)
    visitor_phone = models.CharField(max_length=20, blank=True)
    visitor_email = models.EmailField(blank=True)
    expires_at = models.DateTimeField()
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


