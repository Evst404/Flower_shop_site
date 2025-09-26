from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from .models import (
    Bouquet, Customer, Courier, Order,
    Consultation, Payment, Florist
)


class BouquetForm(forms.ModelForm):
    class Meta:
        model = Bouquet
        fields = '__all__'
        widgets = {
            'composition': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    form = BouquetForm
    list_display = (
        'name', 'price', 'occasion', 'budget',
        'image_preview', 'created_orders_count'
    )
    list_filter = ('occasion', 'budget')
    search_fields = ('name', 'description', 'composition')
    list_editable = ('price', 'occasion', 'budget')
    list_per_page = 25
    ordering = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return 'Нет изображения'

    image_preview.short_description = 'Превью'

    def created_orders_count(self, obj):
        return obj.orders.count()

    created_orders_count.short_description = 'Кол-во заказов'


class OrderInline(admin.TabularInline):
    model = Order
    extra = 1
    fields = ('bouquet', 'delivery_address', 'delivery_time', 'courier', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'orders_count')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('phone_number',)
    inlines = [OrderInline]
    list_per_page = 25
    ordering = ('first_name',)

    def orders_count(self, obj):
        return obj.order_set.count()

    orders_count.short_description = 'Кол-во заказов'


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'telegram_chat_id', 'assigned_orders_count')
    search_fields = ('name', 'phone_number', 'telegram_chat_id')
    list_filter = ('phone_number',)
    list_per_page = 25
    ordering = ('name',)

    def assigned_orders_count(self, obj):
        return obj.order_set.count()

    assigned_orders_count.short_description = 'Назначено заказов'


def assign_courier(modeladmin, request, queryset):
    courier_id = request.POST.get('courier_id')
    if courier_id:
        courier = Courier.objects.get(id=courier_id)
        queryset.update(courier=courier)
        modeladmin.message_user(
            request,
            f"Курьер {courier.name} назначен на выбранные заказы."
        )


assign_courier.short_description = "Назначить курьера на выбранные заказы"


class AssignCourierForm(forms.Form):
    courier = forms.ModelChoiceField(
        queryset=Courier.objects.all(),
        label="Выберите курьера"
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'bouquet', 'customer', 'customer__phone_number', 'courier',
        'delivery_address', 'delivery_time', 'created_at'
    )
    list_filter = (
        'created_at', 'courier', 'bouquet__occasion', 'bouquet__budget'
    )
    search_fields = (
        'customer__first_name', 'customer__last_name',
        'customer__phone_number', 'delivery_address', 'bouquet__name'
    )
    list_per_page = 25
    ordering = ('-created_at',)
    actions = [assign_courier]

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions['assign_courier'] = (
            assign_courier, 'assign_courier', assign_courier.short_description
        )
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['courier'].queryset = Courier.objects.all()
        return form

    def get_action_form(self, request):
        return AssignCourierForm


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'customer__phone_number', 'florist', 'created_at')
    list_filter = ('created_at', 'florist')
    search_fields = (
        'customer__first_name', 'customer__last_name', 'customer__phone_number'
    )
    list_per_page = 25
    ordering = ('-created_at',)


@admin.register(Florist)
class FloristAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone_number', 'telegram_chat_id',
        'assigned_consultations_count'
    )
    search_fields = ('name', 'phone_number', 'telegram_chat_id')
    list_filter = ('phone_number',)
    list_per_page = 25
    ordering = ('name',)

    def assigned_consultations_count(self, obj):
        return obj.consultation_set.count()

    assigned_consultations_count.short_description = 'Кол-во заявок'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_id', 'status', 'amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'payment_id')
    ordering = ('-created_at',)
    readonly_fields = ('payment_id', 'status', 'amount', 'created_at')
