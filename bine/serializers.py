# -*- coding: UTF-8 -*-
from calendar import timegm
import datetime

from rest_framework import serializers
from django.contrib.auth import update_session_auth_hash
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from bine.models import User, Book, BookNote, BookNoteReply


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'email', 'birthday', 'sex', 'tagline',
                  'created_at', 'updated_on', 'password', 'confirm_password')
        read_only_fields = ('created_at', 'updated_on',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.username)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.tagline = validated_data.get('tagline', instance.tagline)

        instance.save()

        password = validated_data.get('password', None)
        confirm_password = validated_data.get('confirm_password', None)

        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
            instance.save()
            update_session_auth_hash(self.context.get('request'), instance)

        return instance

    def register(self):
        self.save()

        if self.instance:
            payload = jwt_payload_handler(self.instance)  # Include original issued at time for a brand new token,
            # to allow token refresh
            if api_settings.JWT_ALLOW_REFRESH:
                payload['orig_iat'] = timegm(
                    datetime.utcnow().utctimetuple()
                )

            return {
                'token': jwt_encode_handler(payload),
                'user': self.data
            }
        return None


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'photo')
        read_only_fields = ('id', 'username', 'fullname', 'photo')


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book

        fields = ('id', 'category', 'title', 'isbn', 'isbn13', 'author', 'author_etc', 'illustrator', 'translator',
                  'publisher', 'pub_date', 'description', 'photo', 'link')


class BookNoteSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    def update(self, instance, validated_data):
        user_id = self.initial_data.get('user')
        book_id = self.initial_data.get('book')
        if user_id and book_id:
            validated_data['user'] = User.objects.get(pk=user_id)
            validated_data['book'] = Book.objects.get(pk=book_id)
        else:
            raise ValidationError;

        return super(BookNoteSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        user_id = self.initial_data.get('user')
        book_id = self.initial_data.get('book')
        if user_id:
            validated_data['user'] = User.objects.get(pk=user_id)

        if book_id:
            validated_data['book'] = Book.objects.get(pk=book_id)

        instance = BookNote.objects.create(**validated_data)

        instance.save()

        return instance

    class Meta:
        model = BookNote
        fields = ('id', 'user', 'book', 'content', 'read_date_from', 'read_date_to', 'preference',
                  'attach', 'share_to', 'created_at')
        depth = 1


class BookNoteReplySerializerMixin(object):
    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BookNoteReplyViewSerializer
        else:
            return BookNoteReplyWriteSerializer


class BookNoteReplyViewSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()

    class Meta:
        model = BookNoteReply
        fields = ('id', 'user', 'content', 'created_at')


class BookNoteReplyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookNoteReply
        fields = ('book', 'user', 'content')