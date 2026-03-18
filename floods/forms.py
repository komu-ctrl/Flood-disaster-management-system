from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    AMOUNT_CHOICES = [
        (100, "KES 100"),
        (500, "KES 500"),
        (1000, "KES 1000"),
    ]

    preset_amount = forms.ChoiceField(
        choices=AMOUNT_CHOICES, required=False, widget=forms.RadioSelect, label="Preset Amount"
    )

    class Meta:
        model = Donation
        fields = ['donor_name', 'donor_email', 'donor_phone', 'amount', 'message', 'is_anonymous']
        widgets = {
            'donor_name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'}),
            'donor_email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'}),
            'donor_phone': forms.TextInput(attrs={'placeholder': '2547XXXXXXXX', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Custom amount', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your message (optional)', 'class': 'form-control', 'rows': 3}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_donor_phone(self):
        phone = self.cleaned_data.get('donor_phone')
        if phone:
            # Validate phone format
            if not (phone.startswith('254') or phone.startswith('0') or phone.startswith('+')):
                raise forms.ValidationError("Phone number must start with 254, 0, or +254")
        return phone
    
    def clean_amount(self):
        preset = self.cleaned_data.get('preset_amount')
        custom = self.cleaned_data.get('amount')
        
        if preset:
            return int(preset)
        elif custom:
            try:
                amount = int(custom)
                if amount < 10:
                    raise forms.ValidationError("Minimum donation is KES 10")
                return amount
            except (ValueError, TypeError):
                raise forms.ValidationError("Please enter a valid amount")
        else:
            raise forms.ValidationError("Please choose a preset amount or enter a custom amount")