from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_price = serializers.DecimalField(source='book.price', read_only=True, max_digits=10, decimal_places=2)
    book_cover = serializers.CharField(source='book.cover_url', read_only=True, allow_null=True)
    book_stock = serializers.IntegerField(source='book.stock', read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)

    class Meta:
        model = CartItem
        fields = [
            'id', 'book_id', 'book_title', 'book_author',
            'book_price', 'book_cover', 'book_stock',
            'quantity', 'subtotal'
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'session_id', 'items', 'total_price', 'total_items']
        read_only_fields = ['session_id']


class CartAddItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


class CartUpdateQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=True, min_value=1)
