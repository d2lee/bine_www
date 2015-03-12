import datetime
from functools import reduce
import os

from django.contrib.auth import authenticate
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase
from rest_framework import status
from rest_framework_jwt.utils import jwt_decode_handler

from bine.models import User, School
from bine.serializers import UserSerializer


class UserViewTestCase(TestCase):
    def setUp(self):
        self.user_data = []
        self.users = []
        for i in range(0, 10):
            username = 'kdhong{0}'.format(str(i))
            email = '{0}@outlook.com'.format(username)
            user_data = {'username': username,
                         'fullname': '홍길동' + str(i),
                         'email': email,
                         'sex': 'M',
                         'birthday': '2000-05-30',
                         'password': 'password123', }
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                self.users.append(user)
                self.user_data.append(user_data)

        self.assertEqual(len(self.users), 10)
        self.assertEqual(len(self.user_data), 10)

        # set up friendship
        # user0 has 4 friends (2 requested from user1, 2 requested from others)
        # user0 has 2 friends waiting for approval
        self.users[0].add_friend(self.users[1])
        self.users[1].approve_friend(self.users[0])
        self.users[0].add_friend(self.users[2])
        self.users[2].approve_friend(self.users[0])

        self.users[3].add_friend(self.users[0])
        self.users[0].approve_friend(self.users[3])
        self.users[4].add_friend(self.users[0])
        self.users[0].approve_friend(self.users[4])

        self.users[5].add_friend(self.users[0])
        self.users[6].add_friend(self.users[0])

        self.users[1].add_friend(self.users[7])
        self.users[7].approve_friend(self.users[1])
        self.users[1].add_friend(self.users[8])
        self.users[8].approve_friend(self.users[1])

        self.users[2].add_friend(self.users[7])
        self.users[2].approve_friend(self.users[7])

        # login to get token
        self.current_user_data = {'username': 'kdhong0',
                                  'password': 'password123'}

        self.current_user = self.users[0]

        url = '/api/auth/login/'
        resp = self.client.post(url, self.current_user_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data.get('token')
        self.auth = 'JWT {0}'.format(token)

    def test_user_search(self):
        # success test with valid query
        url = '/api/user/?q=kdhong'
        resp = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 5)  # 8 because current user and his friends are not counted

        # fail test with invalid query (too short)
        url = '/api/user/?q=k'
        resp = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_info(self):
        def compare_data(key):
            user_dict = self.current_user.__dict__

            if type(user_dict.get(key)) == datetime.date:
                return user_dict.get(key).isoformat() == resp.data.get(key)
            elif type(user_dict.get(key)) == ImageFieldFile:
                return (user_dict.get(key) or '') == resp.data.get(key)
            else:
                return user_dict.get(key) == resp.data.get(key)

        # success test
        resp = self.get_current_user_data()

        check_list = list(map(lambda x: compare_data(x), resp.data))
        is_passed = reduce(lambda a, b: a and b, check_list)
        self.assertTrue(is_passed, 'success test to verify fields')
        self.assertEqual(len(check_list), 13, 'success test to verify the count of fields')

        # failure test to request with wrong userid like username
        url = '/api/user/{0}/'.format(self.current_user.username)
        resp = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND,
                         'failure test to request current user info with wrong id')

        # failure test to request other user info
        url = '/api/user/{0}/'.format(self.users[2].id)
        resp = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED,
                         'failure test to request other user info')

        # failure test to request user information with query
        url = '/api/user/{0}/?q={1}'.format(self.current_user.id, 'kdhong')
        resp = self.client.get(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,
                         'failure test to request user information with query')

    def test_user_invalid_update(self):
        url = '/api/user/{0}/?action=xxx'.format(self.current_user.id)
        resp = self.client.post(url, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,
                         'failure test with updating user with wrong action value')

    def test_update_user_photo(self):
        # success test
        url = '/api/user/{0}/?action=photo'.format(self.current_user.id)

        test_photo_path = "{0}/test.jpg".format(os.path.dirname(__file__))

        with open(test_photo_path, 'rb') as fp:
            resp = self.client.post(url, {'file': fp}, HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(resp.status_code, status.HTTP_200_OK, 'success test to upload user photo')

        user = User.objects.get(pk=self.current_user.id)
        photo = user.photo
        self.assertNotEquals(photo, None, 'success test to upload user photo')
        self.assertEqual(photo.url, resp.data.get('photo'), 'success test to upload user photo')

        # failure test with uploading photo with different user
        url = '/api/user/{0}/?action=photo'.format(self.users[2].id)

        test_photo_path = "{0}/test.jpg".format(os.path.dirname(__file__))

        with open(test_photo_path, 'rb') as fp:
            resp = self.client.post(url, {'file': fp}, HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED,
                         'failure test with uploading photo with different user')
        pass

    def get_current_user_data(self):
        url = '/api/user/{0}/'.format(self.current_user.id)
        return self.client.get(url, HTTP_AUTHORIZATION=self.auth)

    def update_user(self, data):
        for x in data:
            if data[x] is None:
                data[x] = ''

        url = '/api/user/{0}/'.format(self.current_user.id)
        resp = self.client.post(url, data, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.current_user.id)

        user = authenticate(username=self.current_user.username, password=data.get('np'))
        self.assertNotEquals(user, None, 'password check failed!')

    def test_update_user_without_school(self):
        resp = self.get_current_user_data()

        data = resp.data.copy()
        list(map(lambda x: resp.data[x] or '', data))
        data['fullname'] = '뉴홍길동'
        data['email'] = 'kdhongxxx@outlook.com'
        data['birthday'] = '2006-05-30'
        data['sex'] = 'M'
        data['company'] = '테스트학교'
        data['target_from'] = '2015-03-16'
        data['target_to'] = '2015-12-30'
        data['target_books'] = 100
        data['cp'] = self.current_user_data.get('password')
        data['np'] = '123password'

        self.update_user(data)

    def test_update_user_with_school(self):
        school = School.objects.create(level='A', name="서울일원초등학교", address="서울특별시 강남구 영동대로4길 20 (일원동.일원초등학교)")
        school.save()

        resp = self.get_current_user_data()

        data = resp.data.copy()
        data['fullname'] = '뉴홍길동'
        data['email'] = 'kdhongxxx@outlook.com'
        data['birthday'] = '2006-05-30'
        data['sex'] = 'M'
        data['company'] = '테스트학교'
        data['target_from'] = '2015-03-16'
        data['target_to'] = '2015-12-30'
        data['target_books'] = 100
        data['cp'] = self.current_user_data.get('password')
        data['np'] = '123password'
        data['school'] = school.id

        self.update_user(data)

    def test_update_user_with_invalid_data(self):
        url = '/api/user/{0}/'.format(self.current_user.id)

        # failure test to update user with null parameter
        invalid_data = {'fullname': '',
                        'email': '',
                        'sex': '',
                        'birthday': '',
                        'cp': '',
                        'np': '', }
        resp = self.client.post(url, invalid_data, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'failure test: updating user with null param.')

        # failure test to update user with invalid parameter
        invalid_data = {'fullname': '뉴홍길동fdsafdskafjdsaklfjasl;fjd#?&sadfka',
                        'email': 'kdhongxxx@outlook.',
                        'sex': 'Ffdsa',
                        'birthday': '2005-0fdsa5-20',
                        }
        resp = self.client.post(url, invalid_data, HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,
                         'failure test to update user with invalid parameter.')


class StartPageTestCase(TestCase):
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
        # self.assertEqual(api_settings.JWT_EXPIRATION_DELTA, datetime.timedelta(seconds=300))
        pass

    def test_index(self):
        """
            첫 페이지가 제대로 보이는지 테스트하는 루틴
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.templates[0].name, 'bine.html')

    def test_check_duplication(self):
        url = '/api/auth/check/'

        user = self.create_user()

        # success test
        input_data1 = {'username': user.username}
        resp = self.client.post(url, input_data1)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # failure test
        input_data2 = {'username': 'xxxxxx'}
        resp = self.client.post(url, input_data2)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        pass

    def test_register(self):
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




