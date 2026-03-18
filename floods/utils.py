import requests
import base64
from datetime import datetime
from django.conf import settings
import json

class MpesaGateway:
    """M-Pesa API Gateway"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        # Use sandbox URL for testing
        self.base_url = "https://sandbox.safaricom.co.ke"
        
    def get_access_token(self):
        """Get M-Pesa API access token"""
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode('utf-8')
        
        headers = {"Authorization": f"Basic {auth}"}
        
        try:
            response = requests.get(auth_url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            raise
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        access_token = self.get_access_token()
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode('utf-8')
        
        # Clean phone number (remove 0 or +254)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Prepare request data
        stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference[:12],  # Max 12 chars
            "TransactionDesc": transaction_desc[:13]  # Max 13 chars
        }
        
        try:
            response = requests.post(stk_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in STK push: {e}")
            raise