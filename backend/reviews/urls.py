from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewAdminViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'admin/reviews', ReviewAdminViewSet, basename='admin-review')

urlpatterns = [
    path('', include(router.urls)),
]
