from django.contrib import admin
from django.urls import path, include
from noticias.views import webhook_receiver
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('noticias.urls')),
    path('webhook/noticias/', webhook_receiver, name='webhook-receiver'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]