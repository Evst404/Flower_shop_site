from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404

from .models import Bouquet, Consultation, Customer, Order
from .forms import ConsultationForm, CustomerForm, OrderForm, PaymentForm


def index(request):
    recommended_bouquets = Bouquet.objects.all()[:3]
    consultation_form = ConsultationForm()

    if request.method == 'POST' and 'consultation_submit' in request.POST:
        consultation_form = ConsultationForm(request.POST)
        if consultation_form.is_valid():
            consultation = consultation_form.save()
            send_mail(
                'Новая заявка на консультацию',
                f'Имя: {consultation.name}\n'
                f'Телефон: {consultation.phone_number}\n'
                f'Email: {consultation.email}',
                settings.EMAIL_HOST_USER,
                ['florist@projectprimeflowershop.ru'],
                fail_silently=True,
            )
            consultation.florist_notified = True
            consultation.save()
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('index')
        messages.error(request, 'Ошибка в заполнении формы.')

    return render(
        request,
        'index.html',
        {
            'recommended_bouquets': recommended_bouquets,
            'consultation_form': consultation_form,
        },
    )


def catalog(request):
    bouquets = Bouquet.objects.all()
    return render(request, 'catalog.html', {'bouquets': bouquets})


def card(request, bouquet_id):
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
    except Bouquet.DoesNotExist:
        raise Http404("Букет не найден")

    consultation_form = ConsultationForm()

    if request.method == 'POST' and 'consultation_submit' in request.POST:
        consultation_form = ConsultationForm(request.POST)
        if consultation_form.is_valid():
            consultation = consultation_form.save()
            send_mail(
                'Новая заявка на консультацию',
                f'Имя: {consultation.name}\n'
                f'Телефон: {consultation.phone_number}\n'
                f'Email: {consultation.email}',
                settings.EMAIL_HOST_USER,
                ['florist@projectprimeflowershop.ru'],
                fail_silently=True,
            )
            consultation.florist_notified = True
            consultation.save()
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('card', bouquet_id=bouquet.id)
        messages.error(request, 'Ошибка в заполнении формы.')

    return render(
        request,
        'card.html',
        {'bouquet': bouquet, 'consultation_form': consultation_form},
    )


def consultation(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save()
            send_mail(
                'Новая заявка на консультацию',
                f'Имя: {consultation.name}\n'
                f'Телефон: {consultation.phone_number}\n'
                f'Email: {consultation.email}',
                settings.EMAIL_HOST_USER,
                ['florist@projectprimeflowershop.ru'],
                fail_silently=True,
            )
            consultation.florist_notified = True
            consultation.save()
            messages.success(request, 'Заявка успешно отправлена!')
            return redirect('index')
        messages.error(request, 'Ошибка в заполнении формы.')
    else:
        form = ConsultationForm()

    return render(request, 'consultation.html', {'form': form})


def order(request, bouquet_id):
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
    except Bouquet.DoesNotExist:
        raise Http404("Букет не найден")

    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        order_form = OrderForm(request.POST)
        if customer_form.is_valid() and order_form.is_valid():
            customer = customer_form.save()
            order = order_form.save(commit=False)
            order.customer = customer
            order.bouquet = bouquet
            order.save()
            messages.success(request, 'Заказ создан! Перейдите к оплате.')
            return redirect('order_step', order_id=order.id)
        messages.error(
            request,
            'Ошибка в заполнении формы. Проверьте данные.',
        )
    else:
        customer_form = CustomerForm()
        order_form = OrderForm()

    return render(
        request,
        'order.html',
        {
            'customer_form': customer_form,
            'order_form': order_form,
            'bouquet': bouquet,
        },
    )


def order_step(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Заказ не найден")

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            order.order_status = 'Собираем ваш букет'
            order.save()
            send_mail(
                'Новый заказ',
                f'Букет: {order.bouquet.name}\n'
                f'Адрес: {order.delivery_address}\n'
                f'Время: {order.delivery_time}\n'
                f'Клиент: {order.customer.first_name} {order.customer.last_name}\n'
                f'Телефон: {order.customer.phone_number}',
                settings.EMAIL_HOST_USER,
                ['courier@projectprimeflowershop.ru'],
                fail_silently=True,
            )
            messages.success(
                request,
                'Оплата успешно обработана! Заказ принят.',
            )
            return redirect('index')
        messages.error(
            request,
            'Ошибка в данных оплаты. Проверьте введенные данные.',
        )
    else:
        payment_form = PaymentForm()

    return render(
        request,
        'order-step.html',
        {'payment_form': payment_form, 'order': order},
    )


def quiz(request):
    if request.method == 'POST':
        occasion = request.POST.get('occasion')
        if occasion:
            request.session['occasion'] = occasion
            return redirect('quiz_step')

    occasions = Bouquet.OCCASIONS
    return render(request, 'quiz.html', {'occasions': occasions})


def quiz_step(request):
    if request.method == 'POST':
        budget = request.POST.get('budget')
        occasion = request.session.get('occasion', 'Без повода')
        bouquets = Bouquet.objects.filter(occasion=occasion)

        if budget == 'До 1 000 руб':
            bouquet = bouquets.filter(price__lte=1000).first()
        elif budget == '1 000 - 5 000 руб':
            bouquet = bouquets.filter(price__gte=1000, price__lte=5000).first()
        elif budget == 'от 5 000 руб':
            bouquet = bouquets.filter(price__gte=5000).first()
        else:
            bouquet = bouquets.first() or Bouquet.objects.first()

        if bouquet:
            return redirect('result', bouquet_id=bouquet.id)

        messages.error(
            request,
            'Нет подходящих букетов для выбранного события и бюджета.',
        )
        return redirect('quiz_step')

    return render(request, 'quiz-step.html')


def result(request, bouquet_id):
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
    except Bouquet.DoesNotExist:
        raise Http404("Букет не найден")

    return render(request, 'result.html', {'bouquet': bouquet})
