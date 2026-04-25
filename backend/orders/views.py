import uuid
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from carts.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)


def generate_order_number():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = uuid.uuid4().hex[:6].upper()
    return f'ORD{timestamp}{random_suffix}'


def get_or_create_cart(request):
    session_id = request.COOKIES.get('cart_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())

    cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart, session_id


class OrderViewSet(viewsets.ViewSet):
    lookup_field = 'id'

    def list(self, request):
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        try:
            order = Order.objects.prefetch_related('items').get(id=id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart, session_id = get_or_create_cart(request)
        cart_items = CartItem.objects.select_related('book').filter(cart=cart)

        if not cart_items.exists():
            return Response({'error': '购物车为空'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.book.stock < item.quantity:
                return Response(
                    {'error': f'图书《{item.book.title}》库存不足，当前库存: {item.book.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            order = Order.objects.create(
                order_number=generate_order_number(),
                session_id=session_id,
                status=Order.STATUS_PENDING,
                shipping_address=serializer.validated_data['shipping_address'],
                contact_name=serializer.validated_data['contact_name'],
                contact_phone=serializer.validated_data['contact_phone'],
                total_amount=cart.total_price,
            )

            order_items = []
            for item in cart_items:
                book = item.book
                book.stock -= item.quantity
                book.save()

                order_items.append(OrderItem(
                    order=order,
                    book=book,
                    book_title=book.title,
                    book_author=book.author,
                    book_isbn=book.isbn,
                    price=book.price,
                    quantity=item.quantity,
                    subtotal=book.price * item.quantity,
                ))

            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()

        order.refresh_from_db()
        order_serializer = OrderDetailSerializer(order)
        response = Response(order_serializer.data, status=status.HTTP_201_CREATED)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=True, methods=['put', 'patch'], url_path='status')
    def update_status(self, request, id=None):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response({'error': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order.status = serializer.validated_data['status']
        order.save()

        order_serializer = OrderDetailSerializer(order)
        return Response(order_serializer.data)

    @action(detail=False, methods=['get'], url_path='my')
    def my_orders(self, request):
        session_id = request.COOKIES.get('cart_session_id')
        if not session_id:
            return Response([])

        orders = Order.objects.filter(session_id=session_id).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
