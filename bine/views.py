# -*- coding: UTF-8 -*-
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, \
    HTTP_200_OK
from rest_framework.response import Response
from django.views.generic.base import View
from django.shortcuts import render
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import refresh_jwt_token, jwt_response_payload_handler

from bine.models import BookNote, BookNoteReply, User, Book, BookNoteLikeit, School
from bine.serializers import BookSerializer, BookNoteSerializer, UserSerializer, FriendSerializer, SchoolSerializer
from bine_www import settings


@api_view(('GET',))
@permission_classes((IsAuthenticated, ))
def get_book_search_key(request):
    key = settings.BOOK_SEARCH_KEY
    return JsonResponse(data={'key': key})


class IndexView(View):
    @staticmethod
    def get(request):
        return render(request, 'bine.html')


# noinspection PyMethodMayBeStatic
class AuthView(APIView):
    permission_classes = (AllowAny,)

    def check_username(self, username):
        """
            if duplication, return OK with no content -status code:204; otherwise,
            return not found error -status code:404.
        """

        if username and len(username) >= 5:
            users = User.objects.filter(username=username)
            if len(users) == 1:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        pass

    def register(self, request_data):
        serializer = UserSerializer(data=request_data)

        if serializer.is_valid():
            data = serializer.register()
            if data:
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        pass

    def login(self, request):
        serializer = JSONWebTokenSerializer(data=request.DATA)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, action):
        if action == 'check':
            username = request.data.get('username')
            return self.check_username(username)
        elif action == 'login':
            return self.login(request)
        elif action == 'register':
            return self.register(request.data)
        elif action == 'refresh':
            return refresh_jwt_token(request)
        pass


# noinspection PyAttributeOutsideInit
class UserView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser,)

    post_actions = ('photo')

    @staticmethod
    def get(request, pk=None):
        query = request.GET.get('q', None)
        if pk and query:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if pk:
            user = User.objects.get(pk=pk)
            if user != request.user:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                serializer = UserSerializer(user)
        else:
            if not (query and len(query) >= 2):
                return Response(status=HTTP_400_BAD_REQUEST)

            users = request.user.search(query)
            serializer = UserSerializer(users, many=True)

        return Response(serializer.data, content_type="application/json")

    def update_photo(self, request):
        data = {'photo': request.FILES.get('file', None)}
        serializer = UserSerializer(self.user, data=data)
        if serializer.is_valid():
            user = serializer.save()
            if user and user.photo:
                data = {'photo': user.photo.url}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def check_invalid_password(self, request):
        # intentionally changed the password name to cp and np for strong security
        current_password = request.data.get("cp", None)
        new_password = request.data.get("np", None)

        # change the key name of password to serialize
        if current_password:
            request.DATA.pop('np')

        if new_password:
            request.DATA.pop('cp')

        # if current_password and new_password is not defined, we can proceed update
        # otherwise, we need to check password with current password.
        if not (current_password and new_password):
            return False

        username = self.user.username

        if authenticate(username=username, password=current_password):
            request.DATA['password'] = new_password
            return False
        else:
            return True

    def update_user(self, request):
        def remove_photo_from_request(request):
            if request.data.get('photo') is not None:
                request.DATA.pop('photo')

        if self.check_invalid_password(request):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        remove_photo_from_request(request)

        serializer = UserSerializer(self.user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    def check_user_authentication(self, request, pk):
        self.user = None
        try:
            user = User.objects.get(pk=pk)
            if user == request.user:
                self.user = user
        except User.DoesNotExist:
            self.user = None

    def check_invalid_parameters_for_post(self, request, pk):
        self.action = request.GET.get('action', None)
        return pk is None or (self.action and self.action not in self.post_actions)

    def post(self, request, pk):
        if self.check_invalid_parameters_for_post(request, pk):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # PK 값으로 현재 사용자와 로그인 사용자가 같은지 확인한다.
        self.check_user_authentication(request, pk)
        if self.user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if self.action == 'photo':
            return self.update_photo(request)
        else:
            return self.update_user(request)
        pass


class BookDetail(APIView):
    @staticmethod
    def get(request, pk=None, isbn13=None):
        if pk:
            try:
                book = Book.objects.get(pk=pk)
            except Book.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        elif isbn13:
            try:
                book = Book.objects.get(isbn13=isbn13)
            except Book.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = BookSerializer(book)
        return Response(serializer.data)


class BookList(APIView):
    @staticmethod
    def get(request):
        """
        title = request.GET.get('title', None)

        if title is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(title__icontains=title)[:10]
        """
        books = Book.objects.all().order_by('-created_at')
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)


class FriendView(APIView):
    @staticmethod
    def get(request):
        user = request.user

        action = request.GET.get('type', None)

        if action == 'count':
            count_list = user.get_friends_count();
            return Response(count_list)

        if action == 'recommend':
            friends = user.get_recommended_friends()
        elif action == 'search':
            query = request.data.get('q')
            if query is None:
                return Response(status=HTTP_400_BAD_REQUEST)
            friends = user.search_friend(query)
        elif action == 'me':
            friends = user.get_friends_by_me()
        elif action == 'others':
            friends = user.get_friends_by_others()
        elif action == 'confirm':
            friends = user.get_friends()
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

        if action == 'recommend':
            serializer = FriendSerializer(friends, many=True)
        else:
            serializer = UserSerializer(friends, many=True)

        return Response(serializer.data, content_type="application/json")

    @staticmethod
    def put(request, pk):
        friend_id = pk
        friend_status = request.GET.get('status', None)

        if friend_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        friend = User.objects.get(pk=friend_id)
        if friend is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        if friend_status == 'A':
            relation = request.user.approve_friend(friend)
        elif friend_status == 'R':
            relation = request.user.reject_friend(friend)

        if relation:
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request):
        friend_id = request.data.get('friend')

        friend = User.objects.get(pk=friend_id)

        if friend is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        request.user.add_friend(friend)

        return Response(data=friend.to_json())

    @staticmethod
    def delete(request, pk):
        friend_id = pk
        friend = User.objects.get(pk=friend_id)

        if friend is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        request.user.remove_friend(friend)

        return Response(data=friend.to_json())


class BookNoteView(APIView):
    @staticmethod
    def get(request, pk=None):
        if pk:
            try:
                note = BookNote.objects.get(pk=pk)
                if note.user == request.user:
                        serializer = BookNoteSerializer(note)
                else:
                    if note.share_to == 'P':
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                    elif note.share_to == 'F':
                        user_friend_list = note.user.get_friends()
                        if user_friend_list.filter(pk=request.user.pk).exists():
                            serializer = BookNoteSerializer(note)
                        else:
                            return Response(status=status.HTTP_401_UNAUTHORIZED)
                    elif note.share_to == 'A':
                        serializer = BookNoteSerializer(note)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            list_type = request.GET.get('type', None)

            user = request.user

            if list_type == 'count':
                data = user.get_count_list()
                return Response(data=data)

            if list_type == 'all':
                notes = user.get_all_notes()
            elif list_type == 'me':
                notes = user.get_notes()
            else:
                Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = BookNoteSerializer(notes, many=True)

        return Response(serializer.data)

    @staticmethod
    @csrf_exempt
    def post(request, pk=None):
        if pk:
            note = BookNote.objects.get(pk=pk)
            if note is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = BookNoteSerializer(note, data=request.data)
        else:
            # set current user to the user although user is sent from client.
            # request.POST['user'] = request.user.id
            serializer = BookNoteSerializer(data=request.data)

        if serializer.is_valid():
            note = serializer.save()
            if note:
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk):
        note = BookNote.objects.get(pk=pk)
        if note is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        note.delete()

        return Response(status=HTTP_200_OK)


class SchoolView(APIView):
    @staticmethod
    def get(request):
        query = request.GET.get('q', None)

        if query:
            schools = School.objects.filter(name__contains=query)[:10]
            serializers = SchoolSerializer(schools, many=True)
            return Response(serializers.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BookNoteLikeItUpdate(APIView):
    def post(self, request, note_id):
        user = request.user
        note = BookNote.objects.get(pk=note_id)

        if user and note:
            likeit = BookNoteLikeit()
            likeit.user = user
            likeit.note = note
            likeit.save()
            return Response(data={'likeit': note.likeit.count()})
        else:
            return Response(status=HTTP_400_BAD_REQUEST)


class BookNoteReplyList(APIView):
    def get(self, request, note_id):
        if note_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        replies = BookNoteReply.objects.filter(note__pk=note_id)
        json_text = list(map(lambda x: x.to_json(), replies.all()))

        return Response(data=json_text)

    def post(self, request, note_id):
        if note_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        reply = BookNoteReply()
        reply.user = request.user
        reply.note = BookNote.objects.get(pk=note_id)
        reply.content = request.data.get('content')
        reply.save()

        return Response(data=reply.to_json())


class BookNoteReplyDetail(APIView):
    def post(self, request, note_id, reply_id):
        if reply_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        reply = BookNoteReply.objects.get(pk=reply_id)
        if reply is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        reply.content = request.data.get('content')
        reply.save()
        return Response(data=reply.to_json())

    def delete(self, request, note_id, reply_id):
        if reply_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        reply = BookNoteReply.objects.get(pk=reply_id)
        if reply:
            reply.delete()

        return Response(HTTP_200_OK)