from django.db import models
from books.models import Book
from carts.models import Cart


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, '待支付'),
        (STATUS_PAID, '已支付'),
        (STATUS_SHIPPED, '已发货'),
        (STATUS_COMPLETED, '已完成'),
    ]

    order_number = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='订单号')
    session_id = models.CharField(max_length=255, db_index=True, verbose_name='会话ID')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='订单状态'
    )
    shipping_address = models.CharField(max_length=500, verbose_name='收货地址')
    contact_name = models.CharField(max_length=100, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, verbose_name='联系电话')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='订单总金额')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'订单: {self.order_number}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='订单'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='图书'
    )
    book_title = models.CharField(max_length=200, verbose_name='书名')
    book_author = models.CharField(max_length=100, verbose_name='作者')
    book_isbn = models.CharField(max_length=13, blank=True, null=True, verbose_name='ISBN')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='小计')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '订单明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.book_title} x {self.quantity}'

    def save(self, *args, **kwargs):
        if self.subtotal is None and self.price and self.quantity:
            self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
