from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoticiaViewSet, CategoriaViewSet, SubcategoriaViewSet

router = DefaultRouter()
router.register(r'noticias', NoticiaViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'subcategorias', SubcategoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]