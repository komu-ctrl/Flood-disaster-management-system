# This file is deprecated - use MpesaGateway from utils.py instead
# Keeping for backward compatibility

from .utils import MpesaGateway

def get_access_token():
    """Deprecated - use MpesaGateway.get_access_token() instead"""
    gateway = MpesaGateway()
    return gateway.get_access_token()

def stk_push(phone, amount):
    """Deprecated - use MpesaGateway.stk_push() instead"""
    gateway = MpesaGateway()
    return gateway.stk_push(phone, amount, "Donation", "Donation payment") 