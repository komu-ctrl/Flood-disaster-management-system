from django.db import models
from django.contrib.auth.models import User

 add-donation-feature
# Create your models here.
from django.db import models
from django.utils import timezone
import uuid

class Donation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    CURRENCY_CHOICES = [
        ('KES', 'KES'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-PESA'),
        ('CARD', 'Card'),
        ('BANK', 'Bank Transfer'),
    ]
    
    # Personal Information
    donor_name = models.CharField(max_length=255)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20)
    
    # Donation Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='KES')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='MPESA')
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Additional Info
    message = models.TextField(max_length=500, blank=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"

class MpesaTransaction(models.Model):
    """Track M-Pesa STK Push transactions"""
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='mpesa_transactions')
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    response_code = models.CharField(max_length=10)
    response_description = models.TextField()
    customer_message = models.TextField(blank=True)
    
    # Callback Data
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
=======
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
 main
