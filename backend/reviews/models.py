from django.db import models
from books.models import Book


class Review(models.Model):
    user_session_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='用户会话ID'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='图书'
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='评分',
        help_text='1-5分'
    )
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name='评价内容'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '评价'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['user_session_id', 'book']

    def __str__(self):
        return f'{self.book.title} - {self.rating}分'
