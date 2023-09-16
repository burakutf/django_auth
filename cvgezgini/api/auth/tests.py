
from django.conf import settings
from django.urls import reverse
from django.test import RequestFactory

from rest_framework.test import APITestCase,APIClient
from rest_framework import status

from cvgezgini.apps.accounts.models import User,VerifyCode
from cvgezgini.api.auth.views import LoginWithEmailView

UPDATE_PASSWORD_URL = reverse('api:update-password')
FORGOT_PASSWORD_WITH_EMAIL_FIRST_STEP_URL = reverse(
    'api:forgot-password-with-email-first-step'
)
FORGOT_PASSWORD_WITH_EMAIL_SECOND_STEP_URL = reverse(
    'api:forgot-password-with-email-second-step'
)

EMAIL = 'test@example.com'

class RegisterViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("api:register")

    def test_register_valid_data(self):
        data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())
        self.assertFalse("password" in response.data)

class LoginWithEmailTestCase(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.code = "1" * settings.VERIFY_CODE_LENGTH
        self.password= "12345678"
        user=User.objects.create(email=self.email)
        user.set_password(self.password)
        user.save()
    def test_login_with_valid(self):
        request = RequestFactory().post(
            "/api/",
            {
                "email": self.email,
                "password": self.password,
            },
        )
        response = LoginWithEmailView().post(request,format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.data)
    def test_login_with_not_valid(self):
        request = RequestFactory().post(
            "/api/",
            {
                "email": self.email,
                "password": "1234567",
            },
        )
        response = LoginWithEmailView().post(request,format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0].code ,'authorization')


class UpdatePassword(APITestCase):
    def setUp(self) -> None:
        self.password = 'helloword'
        self.user = User.objects.create_user(
            username='newuser', password=self.password
        )
        self.client.force_login(self.user)

    def test_update(self):
        new_password = 'my-new-password'
        res = self.client.put(
            UPDATE_PASSWORD_URL,
            {'old_password': 'wrong-password', 'new_password': new_password},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(new_password))

        res = self.client.put(
            UPDATE_PASSWORD_URL,
            {'old_password': self.password, 'new_password': 'weakpss'},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data[0].code, 'weak-password')
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('weakpss'))

        res = self.client.put(
            UPDATE_PASSWORD_URL,
            {'old_password': self.password, 'new_password': new_password},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))


class ForgotPasswordWithemail(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient(REMOTE_ADDR='100.10.10.10')
        self.user = User.objects.create_user(
            username='newuser', email=EMAIL, password='helloword'
        )

    def test_forgot_password(self):
        res = self.client.post(
            FORGOT_PASSWORD_WITH_EMAIL_FIRST_STEP_URL, {'email': EMAIL}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_password = 'FooBarFooBar'
        self.user.refresh_from_db()
        code = VerifyCode.objects.filter().last().code
        res = self.client.post(
            FORGOT_PASSWORD_WITH_EMAIL_SECOND_STEP_URL,
            {
                'email': EMAIL,
                'code': code,
                'new_password': new_password,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(res.data['detail'],'Şifre başarıyla güncellendi.')
        self.assertTrue(self.user.check_password(new_password))
