from django import forms
from .models import Consultation, Customer, Order
from phonenumber_field.formfields import PhoneNumberField

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['name', 'phone_number', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите Имя', 'class': 'consultation__form_input', 'required': True}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+7 (999) 000 00 00', 'class': 'consultation__form_input order__form_input singUpConsultation__form_input', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш e-mail (необязательно)', 'class': 'consultation__form_input'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone_number']  
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите Имя', 'class': 'order__form_input', 'required': True}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия (необязательно)', 'class': 'order__form_input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+7 (999) 000 00 00', 'class': 'order__form_input', 'required': True}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        phone_str = str(phone)
        if not phone_str.startswith('+'):
            raise forms.ValidationError("Телефон должен начинаться с '+' и содержать код страны, например, +79991123456.")
        return phone

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_time']
        widgets = {
            'delivery_address': forms.TextInput(attrs={'placeholder': 'Адрес доставки', 'class': 'order__form_input', 'required': True}),
            'delivery_time': forms.Select(choices=[
                ('Как можно скорее', 'Как можно скорее'),
                ('10:00-12:00', '10:00-12:00'),
                ('12:00-14:00', '12:00-14:00'),
                ('14:00-16:00', '14:00-16:00'),
                ('16:00-18:00', '16:00-18:00'),
                ('18:00-20:00', '18:00-20:00'),
            ], attrs={'class': 'order__form_input', 'required': True}),
        }

class PaymentForm(forms.Form):
    card_num = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'placeholder': 'Введите номер', 'class': 'order__form_input orderStep_form_input', 'required': True}))
    card_mm = forms.CharField(max_length=2, widget=forms.TextInput(attrs={'placeholder': 'ММ', 'class': 'order__form_input orderStep_form_input', 'required': True}))
    card_gg = forms.CharField(max_length=2, widget=forms.TextInput(attrs={'placeholder': 'ГГ', 'class': 'order__form_input orderStep_form_input', 'required': True}))
    card_fname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Имя владельца', 'class': 'order__form_input orderStep_form_input', 'required': True}))
    card_cvc = forms.CharField(max_length=3, widget=forms.TextInput(attrs={'placeholder': 'CVC', 'class': 'order__form_input orderStep_form_input', 'required': True}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'pochta@mail.ru', 'class': 'order__form_input orderStep_form_input'}))