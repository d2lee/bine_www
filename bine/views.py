# -*- coding: UTF-8 -*-
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, \
    HTTP_200_OK
from rest_framework.response import Response
from django.views.generic.base import View
from django.shortcuts import render
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, jwt_response_payload_handler

from bine.models import BookNote, BookNoteReply, User, Book, BookNoteLikeit, School
from bine.serializers import BookSerializer, BookNoteSerializer, UserSerializer, FriendSerializer, SchoolSerializer


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.register()
        if data:
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    pass


@api_view(['POST'])
@permission_classes((AllowAny, ))
def check_username_duplication(request):
    """
        if duplication, return OK with no content -status code:204; otherwise,
        return not found error -status code:404.
    """

    username = request.data.get('username')
    if username and len(username) >= 5:
        users = User.objects.filter(username=username)
        if len(users) == 1:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IndexView(View):
    @staticmethod
    def get(request):
        return render(request, 'bine.html')


class AuthView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def check_username(username):
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

    @staticmethod
    def register(request_data):
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

    @staticmethod
    def login(request):
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


class UserView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser,)

    @staticmethod
    def get(request, pk):
        if pk:
            user = User.objects.get(pk=pk)
            if user != request.user:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                serializer = UserSerializer(user)
        else:
            query = request.GET['q']
            if not (query and len(query) >= 2):
                return Response(status=HTTP_400_BAD_REQUEST)

            users = request.user.search(query)
            serializer = UserSerializer(users, many=True)

        return Response(serializer.data, content_type="application/json")

    @staticmethod
    def post(request, pk):
        """
        사용자 정보를 업데이트한다.
        """

        # PK 값으로 현재 사용자와 로그인 사용자가 같은지 확인한다.
        if pk:
            user = User.objects.get(pk=pk)
            if user != request.user:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = request.user

        # 사진을 업로드하는 경우에는 action 값이 photo로 정의되어 있다.
        action = request.GET.get('action', None)
        if action and action == 'photo':
            data = {'photo': request.FILES.get('file', None)}
            serializer = UserSerializer(user, data=data)
            # serializer = UserSerializer(user, files=request.FILES)
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    data = {'photo': user.photo.url}
                    return Response(data=data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.data.get('photo'):
                request.data.pop('photo')  # make sure that photo should be in the json data.

        # 암호를 변경하는 경우엔 current_password값이 현재 암호로 정의되어 있다.
        username = request.data.get('username', None)
        current_password = request.data.get("current_password", None)
        new_password = request.data.get("password", None)
        if username and current_password and new_password:
            user = authenticate(username=username, password=current_password)
            if user is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(status=HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    @staticmethod
    def get(request, pk=None, isbn13=None):
        if pk is not None:
            try:
                book = Book.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if isbn13 is not None:
            try:
                book = Book.objects.get(isbn13=isbn13)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if book:
            serializer = BookSerializer(book)
            return Response(serializer.data)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)


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

        action = request.GET.get('type')

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
    def get(request):
        """
        현재 사용자와 친구들의 책 노트 목록을 보여준다.
        """
        list_type = request.GET.get('type')

        user = request.user

        if list_type == 'all':
            notes = user.get_all_notes()
        elif list_type == 'me':
            notes = user.get_notes()
        else:
            Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(BookNoteSerializer(notes, many=True).data)

    @staticmethod
    def get(request, pk=None):
        if pk:
            try:
                note = BookNote.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = BookNoteSerializer(note)
        else:
            list_type = request.GET.get('type')

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
        query = request.GET.get('q')

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