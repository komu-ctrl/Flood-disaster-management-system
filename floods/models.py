from django.db import models

# Create your models here.
class FloodAlert(models.Model):
    location = models.CharField(max_length=200)
    risk_level = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.location
