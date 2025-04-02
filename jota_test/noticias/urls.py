from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet, CategoryViewSet, SubcategoryViewSet, webhook_receiver

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategories')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', webhook_receiver, name='webhook-receiver'),
]