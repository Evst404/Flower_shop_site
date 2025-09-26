from django import forms
from .models import Customer, Order
from phonenumber_field.formfields import PhoneNumberField


class ConsultationForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Введите Имя', 'class': 'consultation__form_input'}))
    phone = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': '+7 (999) 000 00 00', 'class': 'consultation__form_input'}))


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите Имя', 'class': 'order__form_input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия', 'class': 'order__form_input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+7 (999) 000 00 00', 'class': 'order__form_input'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_time']
        widgets = {
            'delivery_address': forms.TextInput(attrs={'placeholder': 'Адрес доставки', 'class': 'order__form_input'}),
            'delivery_time': forms.TextInput(attrs={'class': 'order__form_input'}),
        }