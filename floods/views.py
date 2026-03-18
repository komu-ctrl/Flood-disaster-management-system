from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import ReliefForm

def home(request):
    return render(request, 'home.html')


def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    return render(request, 'register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('home')


add-donation-feature
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum
from .models import Donation, MpesaTransaction
from .utils import MpesaGateway
import json
import uuid

def donation_page(request):
    """Render the donation page"""
    return render(request, 'donations/index.html')

def donation_success(request, transaction_id):
    """Show donation success page"""
    donation = get_object_or_404(Donation, transaction_id=transaction_id)
    return render(request, 'donations/success.html', {'donation': donation})

@csrf_exempt
def initiate_payment(request):
    """Handle donation form submission and initiate M-Pesa payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create donation record
            donation = Donation.objects.create(
                donor_name=data.get('donorName'),
                donor_email=data.get('donorEmail'),
                donor_phone=data.get('donorPhone'),
                amount=data.get('amount'),
                message=data.get('message', ''),
                is_anonymous=data.get('isAnonymous', False),
                transaction_id=f"DRF-{uuid.uuid4().hex[:8].upper()}"
            )
            
            # Initialize M-Pesa gateway
            mpesa = MpesaGateway()
            
            # Initiate STK push
            response = mpesa.stk_push(
                phone_number=data.get('donorPhone'),
                amount=int(data.get('amount')),
                account_reference=donation.transaction_id,
                transaction_desc="Flood Relief Donation"
            )
            
            if response.get('ResponseCode') == '0':
                # Save M-Pesa transaction details
                MpesaTransaction.objects.create(
                    donation=donation,
                    merchant_request_id=response.get('MerchantRequestID'),
                    checkout_request_id=response.get('CheckoutRequestID'),
                    response_code=response.get('ResponseCode'),
                    response_description=response.get('ResponseDescription'),
                    customer_message=response.get('CustomerMessage', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'STK push sent. Please check your phone.',
                    'transaction_id': donation.transaction_id,
                    'checkout_request_id': response.get('CheckoutRequestID')
                })
            else:
                donation.status = 'FAILED'
                donation.save()
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to initiate payment',
                    'error': response.get('errorMessage', 'Unknown error')
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Server error',
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa payment callback"""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            
            # Extract callback data
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Find and update transaction
            try:
                mpesa_transaction = MpesaTransaction.objects.get(
                    checkout_request_id=checkout_request_id
                )
                
                # Update transaction details
                mpesa_transaction.result_code = result_code
                mpesa_transaction.result_desc = result_desc
                mpesa_transaction.save()
                
                # Update donation status
                donation = mpesa_transaction.donation
                
                if result_code == 0:
                    # Payment successful
                    callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    
                    # Extract metadata
                    amount = None
                    mpesa_receipt = None
                    phone_number = None
                    
                    for item in callback_metadata:
                        if item.get('Name') == 'Amount':
                            amount = item.get('Value')
                        elif item.get('Name') == 'MpesaReceiptNumber':
                            mpesa_receipt = item.get('Value')
                        elif item.get('Name') == 'PhoneNumber':
                            phone_number = item.get('Value')
                    
                    # Update donation
                    donation.status = 'COMPLETED'
                    donation.mpesa_receipt_number = mpesa_receipt
                    if amount:
                        donation.amount = amount
                    donation.save()
                    
                    # TODO: Send confirmation email/SMS
                    
                else:
                    # Payment failed
                    donation.status = 'FAILED'
                    donation.save()
                
            except MpesaTransaction.DoesNotExist:
                print(f"Transaction not found: {checkout_request_id}")
            
            # Always return success to M-Pesa
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
            
        except Exception as e:
            print(f"Callback error: {str(e)}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Error'})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

def get_donation_stats(request):
    """Get donation statistics for the frontend"""
    if request.method == 'GET':
        try:
            completed_donations = Donation.objects.filter(status='COMPLETED')
            total_amount = completed_donations.aggregate(total=Sum('amount'))['total'] or 0
            total_donors = completed_donations.count()
            
            recent_donations = completed_donations.order_by('-created_at')[:10].values(
                'donor_name', 'amount', 'created_at', 'is_anonymous'
            )
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_amount': float(total_amount),
                    'total_donors': total_donors
                },
                'recent_donations': list(recent_donations)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

def apply_relief(request):

    if request.method == 'POST':
        form = ReliefForm(request.POST)

        if form.is_valid():
            relief = form.save(commit=False)
            relief.user = request.user
            relief.save()
            return redirect('home')

    else:
        form = ReliefForm()

    return render(request, "apply.html", {'form': form})
 main
