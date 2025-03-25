from django.contrib import admin
from django.urls import path, include
from noticias.views import webhook_receiver
from dj_rest_auth.views import LoginView, LogoutView
from dj_rest_auth.registration.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('noticias.urls')),
    path('webhook/noticias/', webhook_receiver, name='webhook-receiver'),
    path('api/auth/login/', LoginView.as_view(), name='rest_login'),
    path('api/auth/logout/', LogoutView.as_view(), name='rest_logout'),
    path('api/auth/register/', RegisterView.as_view(), name='rest_register'),
]