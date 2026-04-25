from django.db.models import Avg, Count
from rest_framework import serializers
from .models import Category, Book


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_at']


class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'price',
            'stock', 'category', 'category_name', 'cover_url'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'price',
            'stock', 'category', 'category_name', 'cover_url',
            'description', 'created_at', 'updated_at',
            'average_rating', 'review_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg is None:
            return None
        return round(avg, 1)

    def get_review_count(self, obj):
        return obj.reviews.aggregate(Count('id'))['id__count'] or 0
