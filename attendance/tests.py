from django.test import TestCase
from .models import CustomUser

class userTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username="bsmith",email="bsmith@alasfc.ca",password="asdasqweqwe")
    def test_user_data(self):
        user = CustomUser.objects.get(username="bsmith")
        self.assertEqual(user.is_company,False)
