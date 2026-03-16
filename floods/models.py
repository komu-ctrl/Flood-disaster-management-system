from django.db import models
from django.contrib.auth.models import User

class ReliefApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200)
    damage_description = models.TextField()
    people_affected = models.IntegerField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return self.full_name