from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    isbn = models.CharField(max_length=13, blank=True, null=True, verbose_name='ISBN')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    stock = models.PositiveIntegerField(default=0, verbose_name='库存数量')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='分类'
    )
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='封面图片URL')
    description = models.TextField(blank=True, null=True, verbose_name='简介')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title
