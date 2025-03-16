from django.test import TestCase
from .models import CustomUser


class CustomUserTestCase(TestCase):
    def setUp(self):
        # Initializing the test by creating a sample CustomUser instance.
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
    
    def test_custom_user_creation(self):
        # Check if the user is created with the correct attributes
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("testpassword"))