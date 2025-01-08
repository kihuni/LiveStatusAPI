from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail
from django.utils import timezone
from datetime import timedelta
import re

from .models import CustomUser, Role

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create default role
        self.default_role = Role.objects.create(
            name='user',
            description='Default user role'
        )
        
        # Test user data
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'full_name': 'Test User',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_registration_flow(self):
        """Test the complete registration flow"""
        # 1. Register new user
        response = self.client.post(reverse('register'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('tokens' in response.data)
        self.assertTrue('user' in response.data)
        
        # 2. Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        
        # Extract verification token from email
        token_match = re.search(r'/verify-email/([^/\s]+)', email_body)
        self.assertIsNotNone(token_match)
        verification_token = token_match.group(1)
        
        # 3. Verify email
        response = self.client.get(reverse('verify-email', kwargs={'token': verification_token}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Check user is verified
        user = CustomUser.objects.get(email=self.user_data['email'])
        self.assertTrue(user.email_verified)

    def test_login_flow(self):
        """Test the login flow with verified and unverified users"""
        # Create verified user
        user = CustomUser.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            full_name=self.user_data['full_name']
        )
        user.email_verified = True
        user.save()
        
        # Test login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'device_token': 'test-device-token',
            'device_type': 'web'
        }
        
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('tokens' in response.data)
        self.assertTrue('permissions' in response.data)
        
        # Check online status and device token
        user.refresh_from_db()
        self.assertTrue(user.is_online)
        self.assertEqual(user.device_tokens.get('web'), 'test-device-token')

    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Create and login user
        user = CustomUser.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            full_name=self.user_data['full_name'],
            email_verified=True
        )

        response = self.client.post(reverse('login'), {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })

        refresh_token = response.data['tokens']['refresh']

        # Test token refresh
        response = self.client.post(reverse('token_refresh'), {
            'refresh': refresh_token
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_logout(self):
        """Test logout functionality"""
        # Create and login user
        user = CustomUser.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            full_name=self.user_data['full_name'],
            email_verified=True
        )
        
        # Login
        response = self.client.post(reverse('login'), {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'device_token': 'test-token',
            'device_type': 'web'
        })

        # Get token and set authorization header
        token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test logout
        response = self.client.post(reverse('logout'), {'device_type': 'web'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user status
        user.refresh_from_db()
        self.assertFalse(user.is_online)
        self.assertFalse('web' in user.device_tokens)

    def test_profile_update(self):
        """Test profile update functionality"""
        # Create and login user
        user = CustomUser.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password'],
            full_name=self.user_data['full_name'],
            email_verified=True
        )

        # Login and get token
        response = self.client.post(reverse('login'), {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Update profile
        update_data = {
            'full_name': 'Updated Name',
            'bio': 'New bio'
        }

        response = self.client.patch(reverse('profile'), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Name')
        self.assertEqual(response.data['bio'], 'New bio')
