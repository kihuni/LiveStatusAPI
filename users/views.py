from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserProfileUpdateSerializer
)
from .models import Role, CustomUser

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email
        user.send_verification_email()
        
        # Assign default role
        default_role = Role.objects.get_or_create(
            name='user',
            defaults={'description': 'Default user role'}
        )[0]
        user.roles = default_role
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Verification email sent'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.email_verified:
            return Response(
                {'error': 'Please verify your email first'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update online status and last seen
        user.update_online_status(True)
        
        # Handle device token for push notifications
        device_token = request.data.get('device_token')
        if device_token:
            device_type = request.data.get('device_type', 'web')
            user.device_tokens[device_type] = device_token
            user.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'permissions': user.get_permissions()
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        user.update_online_status(False)
        
        # Clear device token if provided
        device_type = request.data.get('device_type', 'web')
        if device_type in user.device_tokens:
            del user.device_tokens[device_type]
            user.save()
        
        return Response({'message': 'Successfully logged out'})
    
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(UserSerializer(user).data)

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, token):
        try:
            user = CustomUser.objects.get(verification_token=token)
            
            # Check token expiration (24 hours)
            if timezone.now() > user.verification_token_created + timezone.timedelta(hours=24):
                return Response(
                    {'error': 'Verification token has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.email_verified = True
            user.verification_token = ''
            user.save()
            
            return Response({'message': 'Email successfully verified'})
            
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ResendVerificationView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.send_verification_email()
        return Response({'message': 'Verification email sent'})
    
    
