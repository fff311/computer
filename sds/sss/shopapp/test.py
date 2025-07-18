from django.test import TestCase
from .models import Role

class SimpleTest(TestCase):
    def test_role_exists(self):
        self.assertTrue(hasattr(Role, 'objects'))