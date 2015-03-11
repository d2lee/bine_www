# -*- coding: UTF-8 -*-
from calendar import timegm
import datetime

from rest_framework import serializers
from django.contrib.auth import update_session_auth_hash, authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, ImageField
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from bine.models import User, Book, BookNote, BookNoteReply, School


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('id', 'level', 'high_school_category', 'name', 'address')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    photo = serializers.FileField(allow_empty_file=False, use_url=False, required=False)
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
                  'created_at', 'updated_on', 'password', 'confirm_password', 'school', 'company',
                  'target_from', 'target_to', 'target_books')
        read_only_fields = ('id', 'username',)
        write_only_fields = ('password', 'confirm_password', )
        depth = 1

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        email = validated_data.get('email', None)
        if email != instance.email:
            instance.email = email
            
        fullname = validated_data.get('fullname', None)
        if fullname != instance.fullname:
            instance.fullname = fullname
            
        birthday = validated_data.get('birthday', None)
        if birthday != instance.birthday:
            instance.birthday = birthday
            
        sex = validated_data.get('sex', None)
        if sex != instance.sex:
            instance.sex = sex

        tagline = validated_data.get('tagline', None)
        if tagline != instance.tagline:
            instance.tagline = tagline

        company = validated_data.get('company', None)
        if company != instance.company:
            instance.company = company
            
        target_from = validated_data.get('target_from', None)
        if target_from != instance.target_from:
            instance.target_from = target_from
            
        target_to = validated_data.get('target_to', None)
        if target_to != instance.target_to:
            instance.target_to = target_to

        target_books = validated_data.get('target_books', None)
        if target_books != instance.target_books:
            instance.target_books = target_books

        instance.photo = validated_data.get('photo', instance.photo)
        school_data = self.initial_data.get('school')
        if school_data:
            school_id = school_data.get('id')
            school = School.objects.get(pk=school_id)
            if school:
                instance.school = school

        instance.save()

        password = validated_data.get('password', None)

        if password:
            instance.set_password(password)

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


class FriendSerializer(serializers.ModelSerializer):
    cnt = serializers.IntegerField(allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'photo', 'birthday', 'sex', 'cnt')
        read_only_fields = ('id', 'username', 'fullname', 'photo', 'birthday', 'sex', 'cnt')


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
