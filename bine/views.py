# -*- coding: UTF-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.http.response import HttpResponseBadRequest
from rest_framework.status import HTTP_400_BAD_REQUEST, \
    HTTP_200_OK
from rest_framework.response import Response
from django.views.generic.base import View
from django.shortcuts import render

from bine.models import BookNote, BookNoteReply, User, Book, BookNoteLikeit, Friendship
from bine.serializers import BookSerializer, BookNoteSerializer, UserSerializer, FriendSerializer


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        response_data = serializer.register()

    if response_data is None:
        return Response(status=HTTP_400_BAD_REQUEST)
    else:
        return Response(response_data)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def check_username_duplication(request, username):
    """
        if duplication, return OK; otherwise, return error.
    """
    # assume that it returns HTTP error if error happens
    User.objects.get(username=username)
    return Response(data={'username': username})


def auth_response_payload_handler(token, user=None):
    return {
        'token': token,
        'user': {'id': user.id, 'fullname': user.fullname, 'sex': user.sex},
    }


class IndexView(View):
    @staticmethod
    def get(request):
        return render(request, 'bine.html')


class UserView(APIView):
    @staticmethod
    def get(request):
        query = request.GET['q']
        if not (query and len(query) >= 2):
            return Response(status=HTTP_400_BAD_REQUEST)

        users = request.user.search(query)

        return Response(UserSerializer(users, many=True).data, content_type="application/json")


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


class BookNoteList(APIView):
    @staticmethod
    def get(request):
        """
        현재 사용자와 친구들의 책 노트 목록을 보여준다.
        """
        type = request.GET['type']

        user = request.user

        if type == 'all':
            notes = user.get_my_and_friends_notes()
        elif type == 'me':
            notes = user.get_notes()
        else:
            Response(status=status.HTTP_400_BAD_REQUEST)

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