from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Bouquet(models.Model):
    name = models.CharField(verbose_name='Название букета', max_length=50, unique=True)
    image = models.ImageField(verbose_name='Изображение букета', upload_to='bouquets/', blank=True)
    price = models.PositiveIntegerField(verbose_name='Цена', default=0)
    description = models.TextField(verbose_name='Описание', blank=True)
    composition = models.TextField(verbose_name='Состав', blank=True)
    OCCASIONS = [
        ('День рождения', 'День рождения'),
        ('Свадьба', 'Свадьба'),
        ('В школу', 'В школу'),
        ('Без повода', 'Без повода'),
        ('Другой повод', 'Другой повод'),
    ]
    occasion = models.CharField(verbose_name='Повод', max_length=50, choices=OCCASIONS, default='Без повода')
    COLORS = [
        ('Без цветовой гаммы', 'Без цветовой гаммы'),
        ('Красные', 'Красные'),
        ('Синие', 'Синие'),
    ]
    color_scheme = models.CharField(verbose_name='Цветовая гамма', max_length=50, choices=COLORS, default='Без цветовой гаммы')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'


class Customer(models.Model):
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50, blank=True)
    phone_number = PhoneNumberField('Номер телефона')
    home_address = models.CharField('Адрес доставки', max_length=256, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE)
    bouquet = models.ForeignKey(Bouquet, verbose_name='Букет', related_name='orders', on_delete=models.CASCADE)
    order_price = models.PositiveIntegerField(verbose_name='Цена заказа', default=0)
    ORDER_STATUSES = [
        ('Заявка обрабатывается', 'Заявка обрабатывается'),
        ('Собираем ваш букет', 'Собираем ваш букет'),
        ('Букет в пути', 'Букет в пути'),
        ('Букет у вас', 'Букет у вас'),
    ]
    order_status = models.CharField(verbose_name='Статус заказа', max_length=50, choices=ORDER_STATUSES, default='Заявка обрабатывается')
    delivery_address = models.CharField(verbose_name='Адрес доставки', max_length=256)
    delivery_date = models.DateField(verbose_name='Дата доставки', null=True, blank=True)
    delivery_time = models.CharField(verbose_name='Время доставки', max_length=30)
    comments = models.TextField(verbose_name='Комментарии', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.bouquet and not self.order_price:
            self.order_price = self.bouquet.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.bouquet} для {self.customer} на {self.delivery_date} {self.delivery_time}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Consultation(models.Model):
    name = models.CharField('Имя', max_length=50)
    phone_number = PhoneNumberField('Номер телефона')
    email = models.EmailField('Email', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    florist_notified = models.BooleanField(default=False)

    def __str__(self):
        return f'Заявка от {self.name} ({self.phone_number})'

    class Meta:
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'