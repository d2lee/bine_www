import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler

from bine.models import User
from bine.serializers import UserSerializer


class TestStartPageTestCase(TestCase):
    def setUp(self):
        self.input_data = {'username': 'kdhong',
                           'fullname': '홍길동',
                           'email': 'kdhong@outlook.com',
                           'sex': 'M',
                           'birthday': '2000-05-30',
                           'password': 'password123', }

    def create_user(self):
        serializer = UserSerializer(data=self.input_data)
        if serializer.is_valid():
            user = serializer.save()
        return user

    def check_returned_user_data(self, user_data, user):
        self.assertNotEqual(user_data, None)

        # check if the returned data must have the following 4 items only.
        self.assertEqual(len(user_data), 4)
        self.assertEqual(user_data.get('id'), user.id)
        self.assertEqual(user_data.get('fullname'), self.input_data.get('fullname'))
        self.assertEqual(user_data.get('sex'), self.input_data.get('sex'))
        self.assertEqual(user_data.get('photo'), '')

    def test_production(self):
        # check if token expiration is set as 5 minutes.
        self.assertEqual(api_settings.JWT_EXPIRATION_DELTA, datetime.timedelta(seconds=300))
        pass

    def test_index(self):
        """
            첫 페이지가 제대로 보이는지 테스트하는 루틴
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.templates[0].name, 'bine.html')

    def test_check_duplication(self):

        user = self.create_user()

        url = '/api/auth/check/'

        # success test
        input_data1 = {'username': user.username}
        resp = self.client.post(url, input_data1)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # failure test
        input_data2 = {'username': 'xxxxxx'}
        resp = self.client.post(url, input_data2)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        pass

    def test_success(self):
        url = '/api/auth/register/'
        resp = self.client.post(url, self.input_data)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # test if data is stored successfully
        user = User.objects.get(username='kdhong')
        self.assertEqual(user.fullname, self.input_data['fullname'])
        self.assertEqual(user.email, self.input_data['email'])
        self.assertEqual(user.sex, self.input_data['sex'])
        self.assertEqual(str(user.birthday), self.input_data['birthday'])

        # check if output sent to client is correct
        output_data = resp.data
        self.assertNotEqual(output_data.get('token'), None)
        self.check_returned_user_data(output_data.get('user'), user)

    def login(self, user=None, data=None):
        url = '/api/auth/login/'

        if user is None:
            user = self.create_user()

        # success login test
        if data is None:
            data = self.input_data

        resp = self.client.post(url, data)

        return resp, user, resp.data

    def test_login(self):
        # check if output sent to client is correct
        resp, user, output_data = self.login()

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertNotEqual(output_data.get('token'), None)

        self.check_returned_user_data(output_data.get('user'), user)

        # test failure case if username is valid but password is mismatched.
        fail_data = {'username': 'kdhong',
                     'password': 'wrong_password'}
        resp, user, output_data = self.login(user, fail_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # test failure case if username is invalid
        fail_data = {'username': 'kdhong123',
                     'password': 'wrong_password'}
        resp, user, output_data = self.login(user, fail_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        # first login to get token
        resp, user, output_data = self.login()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        token = output_data.get('token')
        old_decoded_token = jwt_decode_handler(token)
        self.assertNotEqual(token, None)

        url = '/api/auth/refresh/'
        input_data = {'token': token}
        resp = self.client.post(url, input_data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_token = resp.data.get('token')
        decoded_token = jwt_decode_handler(new_token)
        self.assertEqual(decoded_token.get('user_id'), user.id)
        self.assertEqual(decoded_token.get('username'), user.username)
        self.assertEqual(decoded_token.get('email'), user.email)
        self.assertGreaterEqual(decoded_token.get('exp'), old_decoded_token.get('exp'))




