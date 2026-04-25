from django.db import models
from books.models import Book


class Cart(models.Model):
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'Cart: {self.session_id[:20]}'

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='购物车'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='图书'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '购物车项目'
        verbose_name_plural = verbose_name
        unique_together = ['cart', 'book']

    def __str__(self):
        return f'{self.book.title} x {self.quantity}'

    @property
    def subtotal(self):
        return self.book.price * self.quantity
