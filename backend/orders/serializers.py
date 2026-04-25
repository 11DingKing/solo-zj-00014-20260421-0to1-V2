from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'book_title', 'book_author', 'book_isbn',
            'price', 'quantity', 'subtotal'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_amount', 'shipping_address', 'contact_name',
            'contact_phone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'status', 'total_amount', 'created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'shipping_address', 'contact_name', 'contact_phone',
            'total_amount', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'status', 'total_amount', 'items', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True, max_length=500)
    contact_name = serializers.CharField(required=True, max_length=100)
    contact_phone = serializers.CharField(required=True, max_length=20)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
