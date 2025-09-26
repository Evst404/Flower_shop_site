from django import forms
from .models import Customer, Order

class ConsultationForm(forms.Form):
    name = forms.CharField(max_length=100, label='Имя')
    phone = forms.CharField(max_length=15, label='Телефон')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone_number']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_time']
        widgets = {
            'delivery_time': forms.Select(choices=[
                ('Как можно скорее', 'Как можно скорее'),
                ('10:00-12:00', '10:00-12:00'),
                ('12:00-14:00', '12:00-14:00'),
                ('14:00-16:00', '14:00-16:00'),
                ('16:00-18:00', '16:00-18:00'),
                ('18:00-20:00', '18:00-20:00'),
            ]),
        }