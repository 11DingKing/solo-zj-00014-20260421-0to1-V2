from rest_framework import serializers
from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['book', 'rating', 'content']

    def validate_book(self, value):
        if not value:
            raise serializers.ValidationError('图书不能为空')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'book', 'book_title', 'book_author', 'rating',
            'content', 'created_at', 'is_owner'
        ]
        read_only_fields = ['created_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        session_id = request.COOKIES.get('review_session_id') or request.COOKIES.get('cart_session_id')
        return obj.user_session_id == session_id


class ReviewAdminSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'book', 'book_title', 'book_author', 'user_session_id',
            'rating', 'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user_session_id', 'created_at', 'updated_at']
