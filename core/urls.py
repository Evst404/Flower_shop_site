from django.urls import path
from .views import index, catalog, card, consultation, order, order_step, quiz, quiz_step, result

urlpatterns = [
    path('', index, name='index'),
    path('catalog/', catalog, name='catalog'),
    path('card/<int:bouquet_id>/', card, name='card'),
    path('consultation/', consultation, name='consultation'),
    path('order/<int:bouquet_id>/', order, name='order'),
    path('order/<int:order_id>/step/', order_step, name='order_step'),
    path('quiz/', quiz, name='quiz'),
    path('quiz/step/', quiz_step, name='quiz_step'),
    path('result/<int:bouquet_id>/', result, name='result'),
]