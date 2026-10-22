from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from src.core.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/v1/', include('src.users.urls')),
    path('api/v1/', include('src.customers.urls')),
    path('api/v1/', include('src.products.urls')),
    path('api/v1/', include('src.orders.urls')),
    path('api/v1/', include('src.finance.urls')),
    path('api/v1/orcamento-publico/', include('src.quotes.urls')),
]
