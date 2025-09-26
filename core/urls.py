from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz/step/', views.quiz_step, name='quiz_step'),
    path('result/<int:bouquet_id>/', views.result, name='result'),
    path('catalog/', views.catalog, name='catalog'),
    path('card/<int:bouquet_id>/', views.card, name='card'),
    path('consultation/', views.consultation, name='consultation'),
    path('order/<int:bouquet_id>/', views.order, name='order'),
    path('order_complete/<int:order_id>/', views.order_complete, name='order_complete'),
    path('webhook/yookassa/', views.webhook_yookassa, name='webhook_yookassa'),
    path('stats/', views.stats, name='stats'),
    path('stats/download/', views.stats_download, name='stats_download'),
]