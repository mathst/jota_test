from django.contrib import admin
from django.urls import path, include
from noticias.views import webhook_receiver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('noticias.urls')),
    path('webhook/noticias/', webhook_receiver, name='webhook-receiver'),
]