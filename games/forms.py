from django import forms
from .models import Review, Order

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3}),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ingresa tu dirección completa'
            }),
            'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS)
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_address'].required = True
        self.fields['payment_method'].required = True