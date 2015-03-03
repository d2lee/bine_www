# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.http.response import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, \
    HTTP_200_OK
from rest_framework.response import Response
from django.views.generic.base import View
from django.shortcuts import render
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from bine.models import BookNote, BookNoteReply, User, Book, BookNoteLikeit
from bine.serializers import BookSerializer, BookNoteSerializer, UserSerializer


def get_book(request):
    book = Book.objects.get(pk=request.POST['book'])
    return book


def auth_response_payload_handler(token, user=None):
    return {
        'token': token,
        'user': UserSerializer(user).data,
    }


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, None)


class IndexView(View):
    def get(self, request):
        return render(request, 'bine.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        if not (username and password):
            return JsonResponse(status=HTTP_400_BAD_REQUEST)

        if request.user:
            logout(request)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response(data=user.to_json(), status=HTTP_200_OK)

        return Response(status=HTTP_403_FORBIDDEN)


class Register(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        username = request.data['username']
        fullname = request.data['fullname']
        birthday = request.data['birthday']
        sex = request.data['sex']
        email = request.data['email']
        password = request.data['password']

        # validation code is required here
        user = User.objects.create_user(username=username,
                                        fullname=fullname,
                                        birthday=birthday,
                                        sex=sex,
                                        email=email,
                                        password=password)
        if user is not None:
            serializer = JSONWebTokenSerializer(data=request.DATA)
            if serializer.is_valid():
                token = serializer.object.get('token')
                response_data = auth_response_payload_handler(token, user)
                return Response(response_data)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_403_FORBIDDEN)


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
        title = request.GET.get('title', None)

        if title is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(title__icontains=title)[:10]
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)


class FriendList(APIView):
    def get(self, request, action=None):
        if action is None:
            Response(status=HTTP_400_BAD_REQUEST)

        user = request.user

        if action == 'recommend':
            friends = user.get_recommended_friends()
        elif action == 'search':
            query = request.GET.get('q')
            if query is None:
                return Response(status=HTTP_400_BAD_REQUEST)
            friends = user.search_friend(query)
        elif action is None:
            status = request.GET.get('status')
            if status == 'Y':
                friends = user.get_confirmed_friends()
            elif status == 'N':
                friends = user.get_unconfirmed_friends()
            else:
                return Response(status=HTTP_400_BAD_REQUEST)

        json_text = list(map(lambda x: x.to_json(), friends))
        return Response(data=json_text)

    def put(self, request):
        friend_id = request.data.get('friend')
        status = request.data.get('status')

        if friend_id is None or status is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_200_OK)

    def post(self, request):
        friend_id = request.data.get('friend')

        friend = User.objects.get(pk=friend_id)

        if friend is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        friend.add_friend(request.user, True)

        return Response(data=friend.to_json())

    def delete(self, request, pk):
        friend_id = pk
        friend = User.objects.get(pk=friend_id)

        if friend is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        friend.remove_friend(request.user, True)

        return Response(data=friend.to_json())


class BookNoteList(APIView):
    @staticmethod
    def get(request):
        """
        현재 사용자와 친구들의 책 노트 목록을 보여준다.
        """
        notes = request.user.get_user_and_friend_notes()
        return Response(BookNoteSerializer(notes, many=True).data)

    @staticmethod
    @csrf_exempt
    def post(request):
        # set current user to the user although user is sent from client.
        request.POST['user'] = request.user.id

        serializer = BookNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BookNoteDetail(APIView):
    @staticmethod
    def get(request, pk):
        try:
            note = BookNote.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BookNoteSerializer(note)
        return Response(serializer.data)

    @staticmethod
    def post(request, pk):
        note = BookNote.objects.get(pk=pk)
        if note is None:
            return HttpResponseBadRequest()

        serializer = BookNoteSerializer(instance=note, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        note = serializer.save()

        if note:
            return Response(serializer.data)

    @staticmethod
    def delete(request, pk):
        note = BookNote.objects.get(pk=pk)
        if note is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        note.delete()

        return Response(status=HTTP_200_OK)


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