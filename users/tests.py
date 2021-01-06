from users.models import Profile
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model

class CustomUserTest(TestCase):

    def test_new_user(self):
        db = get_user_model()
        user = db.objects.create_user(
            'username', 'username@example.com', 'password123'
        )
        self.assertEqual(user.email, 'username@example.com')
        self.assertEqual(user.username, 'username')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(str(user), 'username')
        self.assertEqual(user.get_full_name(), '')
        self.assertEqual(user.get_short_name(), '')
        self.assertEqual(user.email_user(
            'Subject Example', 'Here is the message.',
            'from@example.com',
            fail_silently=False,
        ), None)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject Example')

        with self.assertRaises(ValueError):
            db.objects.create_superuser(
            username=None, 
            email='username@example.com', 
            password='password123',
            )
        
        user = db.objects.create_superuser(
            username='username2', 
            email='username2@example.com', 
            password='password123',
            first_name='Test',
            last_name='User'
        )

        self.assertEqual(user.get_full_name(), 'Test User')
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_new_superuser(self):
        db = get_user_model()
        superuser = db.objects.create_superuser(
            'username', 'username@example.com', 'password123'
        )
        self.assertEqual(superuser.email, 'username@example.com')
        self.assertEqual(superuser.username, 'username')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
        self.assertEqual(str(superuser), 'username')

        with self.assertRaises(ValueError):
            db.objects.create_superuser(
            username='username', 
            email='username@example.com', 
            password='password123', 
            is_superuser=False
            )
        with self.assertRaises(ValueError):
            db.objects.create_superuser(
            username='username', 
            email='username@example.com', 
            password='password123', 
            is_staff=False
            )

class ProfileTests(TestCase):
    def test_profile(self):
        db = get_user_model()
        user = db.objects.create_user(
            'username', 'username@example.com', 'password123'
        )
        profile = Profile(user=user, bio='Test Bio')
        self.assertEqual(str(profile), 'username')