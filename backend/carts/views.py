import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from books.models import Book
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartAddItemSerializer,
    CartUpdateQuantitySerializer
)


def get_or_create_cart(request):
    session_id = request.COOKIES.get('cart_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())

    cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart, session_id


class CartViewSet(viewsets.ViewSet):
    lookup_field = 'id'

    def create(self, request):
        cart, session_id = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=False, methods=['get'], url_path='current')
    def current_cart(self, request):
        cart, session_id = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        serializer = CartAddItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': '图书不存在'}, status=status.HTTP_404_NOT_FOUND)

        if book.stock < quantity:
            return Response(
                {'error': f'库存不足，当前库存: {book.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            cart, session_id = get_or_create_cart(request)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                book=book,
                defaults={'quantity': quantity}
            )

            if not created:
                new_quantity = cart_item.quantity + quantity
                if book.stock < new_quantity:
                    return Response(
                        {'error': f'库存不足，当前库存: {book.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=False, methods=['put', 'patch'], url_path='item/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        serializer = CartUpdateQuantitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quantity = serializer.validated_data['quantity']
        cart, session_id = get_or_create_cart(request)

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': '购物车项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        if cart_item.book.stock < quantity:
            return Response(
                {'error': f'库存不足，当前库存: {cart_item.book.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=False, methods=['delete'], url_path='item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        cart, session_id = get_or_create_cart(request)

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': '购物车项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        cart, session_id = get_or_create_cart(request)
        cart.items.all().delete()
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        response = Response(serializer.data)
        response.set_cookie('cart_session_id', session_id, max_age=86400 * 30)
        return response
