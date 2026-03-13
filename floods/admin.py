from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Donation, MpesaTransaction

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 
        'donor_name', 
        'amount', 
        'status_colored', 
        'payment_method', 
        'created_at_formatted',
        'view_receipt'
    ]
    
    list_filter = [
        'status', 
        'payment_method', 
        'currency', 
        'is_anonymous',
        'created_at'
    ]
    
    search_fields = [
        'donor_name', 
        'donor_email', 
        'donor_phone', 
        'transaction_id', 
        'mpesa_receipt_number'
    ]
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Donor Information', {
            'fields': (
                'donor_name', 
                'donor_email', 
                'donor_phone', 
                'is_anonymous'
            )
        }),
        ('Donation Details', {
            'fields': (
                'amount', 
                'currency', 
                'payment_method', 
                'message'
            )
        }),
        ('Transaction Information', {
            'fields': (
                'transaction_id',
                'mpesa_receipt_number',
                'status'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'transaction_id', 
        'created_at', 
        'updated_at',
        'mpesa_receipt_number'
    ]
    
    actions = ['mark_as_completed', 'mark_as_failed', 'export_as_csv']
    
    def status_colored(self, obj):
        colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'FAILED': 'red',
            'REFUNDED': 'gray'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.status
        )
    status_colored.short_description = 'Status'
    status_colored.admin_order_field = 'status'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_formatted.short_description = 'Date'
    created_at_formatted.admin_order_field = 'created_at'
    
    def view_receipt(self, obj):
        if obj.mpesa_receipt_number:
            return format_html(
                '<a href="#" onclick="alert(\'M-PESA Receipt: {}\')">📄 {}</a>',
                obj.mpesa_receipt_number,
                obj.mpesa_receipt_number
            )
        return '-'
    view_receipt.short_description = 'Receipt'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} donations marked as completed.')
    mark_as_completed.short_description = "Mark selected as COMPLETED"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} donations marked as failed.')
    mark_as_failed.short_description = "Mark selected as FAILED"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donations.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Transaction ID', 'Name', 'Email', 'Phone', 
            'Amount', 'Currency', 'Status', 'Date', 'Receipt'
        ])
        
        for donation in queryset:
            writer.writerow([
                donation.transaction_id,
                donation.donor_name,
                donation.donor_email,
                donation.donor_phone,
                donation.amount,
                donation.currency,
                donation.status,
                donation.created_at.strftime("%Y-%m-%d %H:%M"),
                donation.mpesa_receipt_number or ''
            ])
        
        return response
    export_as_csv.short_description = "Export selected as CSV"


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'donation_link',
        'checkout_request_id',
        'result_code',
        'response_description_short',
        'created_at_formatted'
    ]
    
    list_filter = ['result_code', 'created_at']
    
    search_fields = [
        'checkout_request_id', 
        'merchant_request_id',
        'donation__transaction_id'
    ]
    
    readonly_fields = [
        'donation',
        'merchant_request_id',
        'checkout_request_id',
        'response_code',
        'response_description',
        'customer_message',
        'result_code',
        'result_desc',
        'created_at'
    ]
    
    def donation_link(self, obj):
        url = reverse('admin:donations_donation_change', args=[obj.donation.id])
        return format_html('<a href="{}">{} ({})</a>', 
                         url, 
                         obj.donation.donor_name,
                         obj.donation.transaction_id)
    donation_link.short_description = 'Donation'
    
    def response_description_short(self, obj):
        if obj.response_description:
            return obj.response_description[:50] + '...' if len(obj.response_description) > 50 else obj.response_description
        return '-'
    response_description_short.short_description = 'Description'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_formatted.short_description = 'Time'
