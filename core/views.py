from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.db.models import Count
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from yookassa import Configuration, Payment as YooPayment
from .models import Bouquet, Consultation, Customer, Order, Courier, Florist, Payment
from .forms import ConsultationForm, CustomerForm, OrderForm

import random
import requests
import uuid
import json
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
import csv
from io import StringIO
import codecs

def send_telegram_message(chat_id, message):
    url = (
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except RequestException:
        pass

def send_courier_telegram_message(chat_id, message):
    url = (
        f"https://api.telegram.org/bot"
        f"{settings.TELEGRAM_COURIER_BOT_TOKEN}/sendMessage"
    )
    payload = {
        'chat_id': str(chat_id),
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except RequestException:
        pass

def handle_consultation_submission(request, redirect_name, *args, **kwargs):
    form = ConsultationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        customer = Customer.objects.create(
            first_name=form.cleaned_data['name'],
            phone_number=form.cleaned_data['phone']
        )
        florists = Florist.objects.annotate(consultation_count=Count('consultation')).order_by('consultation_count')
        assigned_florist = florists.first() if florists.exists() else None
        consultation = Consultation.objects.create(customer=customer, florist=assigned_florist)  

        occasion = request.session.get('occasion', 'Без повода')
        budget = request.session.get('budget', '1000-5000')

        message = (
            f"<b>Новая заявка на консультацию:</b>\n"
            f"Имя: {customer.first_name}\n"
            f"Телефон: {customer.phone_number}\n"
            f"<b>Результат опроса:</b>\n"
            f"Повод: {occasion}\n"
            f"Бюджет: {budget}"
        )

        florist_chat_id = assigned_florist.telegram_chat_id if assigned_florist and assigned_florist.telegram_chat_id else None
        if florist_chat_id:
            send_telegram_message(florist_chat_id, message)
        elif settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_FLORIST_CHAT_ID:  
            send_telegram_message(settings.TELEGRAM_FLORIST_CHAT_ID, message)

        request.session.pop('occasion', None)
        request.session.pop('budget', None)

        messages.success(request, 'Заявка отправлена!')
        return redirect(redirect_name, *args, **kwargs)
    return form


def index(request):
    recommended_bouquets = Bouquet.objects.order_by('?')[:3]
    form = handle_consultation_submission(request, 'index')
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'index.html',
        {'recommended_bouquets': recommended_bouquets, 'consultation_form': form}
    )


def quiz(request):
    occasions = Bouquet.OCCASIONS
    form = handle_consultation_submission(request, 'quiz')
    if isinstance(form, HttpResponseRedirect):
        return form
    if request.method == 'POST':
        occasion = request.POST.get('occasion')
        if occasion:
            request.session['occasion'] = occasion
            return redirect('quiz_step')
    return render(
        request,
        'quiz.html',
        {'occasions': occasions, 'consultation_form': form}
    )


def quiz_step(request):
    budgets = [
        ('до 1000', 'До 1 000 руб'),
        ('1000-5000', '1 000 - 5 000 руб'),
        ('от 5000', 'от 5 000 руб'),
        ('не имеет значения', 'Не имеет значения'),
    ]
    form = handle_consultation_submission(request, 'quiz_step')
    if isinstance(form, HttpResponseRedirect):
        return form
    if request.method == 'POST':
        budget = request.POST.get('budget')
        occasion = request.session.get('occasion')
        if budget and occasion:
            request.session['budget'] = budget
            bouquets = Bouquet.objects.filter(occasion=occasion)
            if budget != 'не имеет значения':
                bouquets = bouquets.filter(budget=budget)
            if bouquets.exists():
                bouquet = random.choice(bouquets)
                return redirect('result', bouquet_id=bouquet.id)
            return render(
                request,
                'quiz-step.html',
                {'error': 'Нет подходящих букетов.', 'budgets': budgets, 'consultation_form': form}
            )
    return render(
        request,
        'quiz-step.html',
        {'budgets': budgets, 'consultation_form': form}
    )


def result(request, bouquet_id):
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    form = handle_consultation_submission(request, 'result', bouquet_id=bouquet_id)
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'result.html',
        {'bouquet': bouquet, 'consultation_form': form}
    )


def catalog(request):
    bouquets = Bouquet.objects.all()
    paginator = Paginator(bouquets, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = handle_consultation_submission(request, 'catalog')
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'catalog.html',
        {'page_obj': page_obj, 'consultation_form': form}
    )


def card(request, bouquet_id):
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    form = handle_consultation_submission(request, 'card', bouquet_id=bouquet_id)
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'card.html',
        {'bouquet': bouquet, 'consultation_form': form}
    )


def consultation(request):
    form = handle_consultation_submission(request, 'index')
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'consultation.html',
        {'consultation_form': form}
    )


def order(request, bouquet_id):
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        order_form = OrderForm(request.POST)
        if customer_form.is_valid() and order_form.is_valid():
            customer = customer_form.save()
            order = order_form.save(commit=False)
            order.bouquet = bouquet
            order.customer = customer
            couriers = Courier.objects.annotate(order_count=Count('order')).order_by('order_count')
            if couriers.exists():
                order.courier = couriers.first()
            order.save()
            try:
                Configuration.account_id = settings.YOOKASSA_SHOP_ID
                Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
                idempotence_key = str(uuid.uuid4())
                payment = YooPayment.create(
                    {
                        "amount": {"value": str(order.bouquet.price), "currency": "RUB"},
                        "confirmation": {
                            "type": "redirect",
                            "return_url": request.build_absolute_uri(reverse('order_complete', args=[order.id]))
                        },
                        "capture": True,
                        "description": f"Заказ {order.id}: {order.bouquet.name}",
                        "metadata": {"order_id": order.id}
                    },
                    idempotence_key
                )
                Payment.objects.create(
                    order=order,
                    payment_id=payment.id,
                    status=payment.status,
                    amount=order.bouquet.price
                )
                return redirect(payment.confirmation.confirmation_url)
            except Exception as e:
                messages.error(request, f"Ошибка оплаты: {e}")
                return render(
                    request,
                    'order.html',
                    {'bouquet': bouquet, 'customer_form': customer_form, 'order_form': order_form}
                )
        else:
            messages.error(request, 'Проверьте данные.')
    else:
        customer_form = CustomerForm()
        order_form = OrderForm()
    return render(
        request,
        'order.html',
        {'bouquet': bouquet, 'customer_form': customer_form, 'order_form': order_form}
    )


def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = order.payment
    if payment.status == 'succeeded':
        messages.success(request, 'Оплата успешна! Заказ в обработке.')
    else:
        messages.error(request, 'Оплата не удалась.')
    return redirect('index')


@csrf_exempt
def webhook_yookassa(request):
    if request.method == 'POST':
        try:
            event_json = json.loads(request.body)
            if event_json['event'] == 'payment.succeeded':
                payment_id = event_json['object']['id']
                payment_obj = Payment.objects.get(payment_id=payment_id)
                payment_obj.status = 'succeeded'
                payment_obj.save()
                order = payment_obj.order
                courier_chat_id = (
                    order.courier.telegram_chat_id
                    if order.courier and order.courier.telegram_chat_id
                    else settings.TELEGRAM_COURIER_CHAT_ID
                )
                if courier_chat_id:
                    message = (
                        f"<b>Заказ оплачен:</b>\n"
                        f"Букет: {order.bouquet.name}\n"
                        f"Адрес: {order.delivery_address}\n"
                        f"Время: {order.delivery_time}\n"
                        f"Клиент: {order.customer.first_name} {order.customer.last_name or ''}\n"
                        f"Телефон: {order.customer.phone_number}\n"
                        f"Сумма: {payment_obj.amount} руб"
                    )
                    send_courier_telegram_message(courier_chat_id, message)
        except JSONDecodeError:
            return HttpResponse(status=400)
        except RequestException:
            return HttpResponse(status=400)
        return HttpResponse(status=200)
    return HttpResponse(status=400)


@staff_member_required
def stats(request):
    orders_by_bouquet = (
        Order.objects.values('bouquet__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    orders_by_date = (
        Order.objects.extra(select={'date': 'date(created_at)'})
        .values('date')
        .annotate(count=Count('id'))
    )
    orders_by_customer = (
        Order.objects.values('customer__first_name', 'customer__last_name')
        .annotate(count=Count('id'))
    )
    context = {
        'orders_by_bouquet': orders_by_bouquet,
        'orders_by_date': orders_by_date,
        'orders_by_customer': orders_by_customer,
    }
    return render(request, 'stats.html', context)


@staff_member_required
def stats_download(request):
    output = StringIO()
    output.write(codecs.BOM_UTF8.decode('utf-8'))
    writer = csv.writer(output)
    
    writer.writerow(['Тип статистики', 'Категория', 'Количество'])
    for item in Order.objects.values('bouquet__name').annotate(count=Count('id')).order_by('-count'):
        writer.writerow(['Букет', item['bouquet__name'], item['count']])
    for item in Order.objects.extra(select={'date': 'date(created_at)'}).values('date').annotate(count=Count('id')):
        writer.writerow(['Дата', item['date'], item['count']])
    for item in Order.objects.values('customer__first_name', 'customer__last_name').annotate(count=Count('id')):
        writer.writerow(['Клиент', f"{item['customer__first_name']} {item['customer__last_name'] or ''}", item['count']])
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stats.csv"'
    return response