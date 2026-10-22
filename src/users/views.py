from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from .models import User
from .serializers import UserSerializer
from .permissions import ProfileActionPermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('name', 'username')
    serializer_class = UserSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {}
    search_fields = ['name', 'username', 'email']
    ordering_fields = ['name', 'username', 'created_at']


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
