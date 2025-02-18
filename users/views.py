from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from .serializers import UserSerializer



User = get_user_model()


class UserView(generics.ListCreateAPIView):
    """
    API endpoint for listing all users or creating a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]