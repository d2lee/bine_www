# -*- coding: UTF-8 -*-
from calendar import timegm
import datetime

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from bine.commons import auth_response_payload_handler
from bine.models import User, Book, BookNote, BookNoteReply, School


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('id', 'level', 'high_school_category', 'name', 'address')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    photo = serializers.FileField(allow_empty_file=False, use_url=True, required=False)
    email = serializers.EmailField(required=False)
    birthday = serializers.DateField(required=False)
    sex = serializers.ChoiceField(choices=[('M', '남자'), ('F', '여자')], required=False)
    fullname = serializers.CharField(required=False, max_length=80)
    school = SchoolSerializer(required=False, read_only=True)
    tagline = serializers.CharField(max_length=512, required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    target_from = serializers.DateField(required=False)
    target_from = serializers.DateField(required=False)
    target_books = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'email', 'birthday', 'sex', 'tagline', 'photo',
                  'password', 'confirm_password', 'school', 'company',
                  'target_from', 'target_to', 'target_books')
        read_only_fields = ('id', 'username',)
        depth = 1

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        field_count_changed = 0
        for field_name in validated_data:
            if field_name == 'password':
                password = validated_data.get('password', None)
                if password:
                    instance.set_password(password)
                    field_count_changed += 1
            else:
                field_value = validated_data.get(field_name, None)
                if field_value and field_value != getattr(instance, field_name, None):
                    setattr(instance, field_name, field_value)
                    field_count_changed += 1

        school_id = self.initial_data.get('school')
        if school_id:
            school = School.objects.get(pk=school_id)
            if school and school != instance.school:
                instance.school = school
                field_count_changed += 1

        if field_count_changed > 0:
            instance.save()

        # update_session_auth_hash(self.context.get('request'), instance)

        return instance

    def login(self):
        credentials = {
            'username': self.validated_data.get('username', None),
            'password': self.validated_data.get('password', None),
        }

        if all(credentials.values()):
            self.instance = authenticate(**credentials)
            user = self.instance

            if user:
                if not user.is_active:
                    msg = _('사용자 계정이 비활성화되었습니다.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                # Include original issued at time for a brand new token,
                # to allow token refresh
                if api_settings.JWT_ALLOW_REFRESH:
                    payload['orig_iat'] = timegm(
                        datetime.utcnow().utctimetuple()
                    )

                return {
                    'token': jwt_encode_handler(payload),
                    'user': self.data
                }
            else:
                msg = _('사용자 아이디와 암호가 일치하지 않습니다.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('사용자 아이디와 암호를 입력하시기 바랍니다.')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

    def register(self):
        self.save()

        if self.instance:
            payload = jwt_payload_handler(self.instance)  # Include original issued at time for a brand new token,
            # to allow token refresh
            if api_settings.JWT_ALLOW_REFRESH:
                payload['orig_iat'] = timegm(
                    datetime.datetime.utcnow().utctimetuple()
                )

            token = jwt_encode_handler(payload)

            return auth_response_payload_handler(token, self.instance, request)

        return None


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'photo', 'sex')
        read_only_fields = ('id', 'username', 'fullname', 'photo', 'sex')


class FriendSerializer(serializers.ModelSerializer):
    cnt = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'photo', 'birthday', 'sex', 'cnt')
        read_only_fields = ('id', 'username', 'fullname', 'photo', 'birthday', 'sex', 'cnt')


class BookSerializer(serializers.ModelSerializer):
    num_notes = serializers.IntegerField(read_only=True, required=False)
    avg_rating = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Book

        fields = ('id', 'category', 'title', 'isbn', 'isbn13', 'author', 'author_etc', 'illustrator', 'translator',
                  'publisher', 'pub_date', 'description', 'photo', 'link', 'num_notes', 'avg_rating')
        read_only = ('id', 'num_notes', 'avg_rating')


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

        note = super(BookNoteSerializer, self).update(instance, validated_data)
        if note:
            note.book.update_age_level_with_user_birthday(note.user)
        return note

    def create(self, validated_data):
        user_id = self.initial_data.get('user')
        book_id = self.initial_data.get('book')
        if user_id:
            validated_data['user'] = User.objects.get(pk=user_id)

        if book_id:
            validated_data['book'] = Book.objects.get(pk=book_id)

        instance = BookNote.objects.create(**validated_data)

        instance.save()

        if instance:
            instance.book.update_age_level_with_user_birthday(instance.user)

        return instance

    class Meta:
        model = BookNote
        fields = ('id', 'user', 'book', 'content', 'read_date_from', 'read_date_to', 'rating',
                  'attach', 'share_to', 'created_at')
        read_only = 'created_at'
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
