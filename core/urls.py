from django.urls import path
from .views import index, quiz, quiz_step, result, catalog, card, consultation, order, stats, order_complete, webhook_yookassa  


urlpatterns = [
    path('', index, name='index'),
    path('quiz/', quiz, name='quiz'),
    path('quiz/step/', quiz_step, name='quiz_step'),
    path('result/<int:bouquet_id>/', result, name='result'),
    path('catalog/', catalog, name='catalog'),
    path('card/<int:bouquet_id>/', card, name='card'),
    path('consultation/', consultation, name='consultation'),
    path('order/<int:bouquet_id>/', order, name='order'),
    path('stats/', stats, name='stats'),  
    path('order_complete/<int:order_id>/', order_complete, name='order_complete'),  
    path('webhook/yookassa/', webhook_yookassa, name='webhook_yookassa'),  
]