from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
