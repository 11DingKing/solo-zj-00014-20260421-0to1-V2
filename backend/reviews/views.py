import uuid
from django.db import IntegrityError
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from books.models import Book
from .models import Review
from .serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewAdminSerializer
)


def get_or_create_session_id(request):
    session_id = request.COOKIES.get('review_session_id')
    if not session_id:
        session_id = request.COOKIES.get('cart_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


class ReviewPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReviewViewSet(viewsets.ViewSet):
    lookup_field = 'id'
    pagination_class = ReviewPagination

    @action(detail=False, methods=['get'], url_path='book/(?P<book_id>[^/.]+)')
    def list_by_book(self, request, book_id=None):
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': '图书不存在'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(book=book).select_related('book').order_by('-created_at')

        paginator = ReviewPagination()
        page = paginator.paginate_queryset(reviews, request, view=self)

        serializer = ReviewSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='book/(?P<book_id>[^/.]+)/my')
    def my_review(self, request, book_id=None):
        session_id = get_or_create_session_id(request)

        try:
            review = Review.objects.get(
                book_id=book_id,
                user_session_id=session_id
            )
        except Review.DoesNotExist:
            return Response({'has_review': False, 'review': None})

        serializer = ReviewSerializer(review, context={'request': request})
        return Response({'has_review': True, 'review': serializer.data})

    def create(self, request):
        session_id = get_or_create_session_id(request)

        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = Review.objects.create(
                user_session_id=session_id,
                book=serializer.validated_data['book'],
                rating=serializer.validated_data['rating'],
                content=serializer.validated_data.get('content', '')
            )
        except IntegrityError:
            return Response(
                {'error': '您已评价过该书籍'},
                status=status.HTTP_409_CONFLICT
            )

        response_serializer = ReviewSerializer(review, context={'request': request})
        response = Response(response_serializer.data, status=status.HTTP_201_CREATED)

        if not request.COOKIES.get('review_session_id') and not request.COOKIES.get('cart_session_id'):
            response.set_cookie('review_session_id', session_id, max_age=86400 * 365)

        return response

    def destroy(self, request, id=None):
        session_id = get_or_create_session_id(request)

        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({'error': '评价不存在'}, status=status.HTTP_404_NOT_FOUND)

        if review.user_session_id != session_id:
            return Response(
                {'error': '您只能删除自己的评价'},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewAdminViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('book').all().order_by('-created_at')
    serializer_class = ReviewAdminSerializer
    pagination_class = ReviewPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        book_id = request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
