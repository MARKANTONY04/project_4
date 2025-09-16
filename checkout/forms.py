# checkout/forms.py
from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone_number",
            "address_line1",
            "address_line2",
            "city",
            "postcode",
            "country",
        ]
