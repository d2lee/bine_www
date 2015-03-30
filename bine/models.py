# -*- coding: UTF-8 -*-
import datetime

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q, Count, Avg
from django.db.models.fields import CharField, DateField, TextField, \
    DateTimeField
from django.db.models.fields.related import ForeignKey
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill, Anchor
from django.utils import timezone

from bine.utils import get_file_name, get_this_week_range, convert_birthday_to_age_level


class UserManager(BaseUserManager):
    def create_user(self, username, password, is_staff=False, is_superuser=False, **kwargs):
        if not username:
            raise ValueError('Users must have a valid authentication name.')

        if not kwargs.get('email'):
            raise ValueError('User must have a valid email.')

        if not kwargs.get('fullname'):
            raise ValueError('User must have a valid full name.')

        if not kwargs.get('birthday'):
            raise ValueError('User must have a valid birthday.')

        if not kwargs.get('sex'):
            raise ValueError('User must have a valid sex.')

        user = self.model(username=username,
                          email=self.normalize_email(kwargs.get('email')),
                          fullname=kwargs.get('fullname'),
                          birthday=kwargs.get('birthday'),
                          is_staff=is_staff,
                          is_active=True,
                          is_superuser=is_superuser,
                          sex=kwargs.get('sex'))

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **kwargs):
        return self.create_user(username, password, True, True, **kwargs)


class School(models.Model):
    SCHOOL_LEVEL = (
        ('A', '초등학교'),
        ('B', '중학교'),
        ('C', '고등학교'),
        ('D', '특수학교'),
        ('E', '고등기술학교'),
        ('F', '고등공민학교'),
        ('G', '각종학교'),
    )

    level = CharField(max_length=1, choices=SCHOOL_LEVEL, blank=False)

    HIGH_SCHOOL_CATEGORY = (
        ('A', '일반고'),
        ('B', '자율고'),
        ('C', '특성화고(직업)'),
        ('D', '특성화고(대안)'),
        ('E', '특수목적고'),
    )
    high_school_category = CharField(max_length=1, choices=HIGH_SCHOOL_CATEGORY, blank=True)
    city = CharField(max_length=30, null=False)
    name = CharField(max_length=128, null=False)

    SCHOOL_TYPE = (
        ('A', '공립'),
        ('B', '사립'),
        ('C', '국립'),
    )

    type = models.CharField(max_length=1, choices=SCHOOL_TYPE, blank=False)
    zipcode = CharField(max_length=6, null=False)
    address = CharField(max_length=512, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'schools'


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    email = models.EmailField(unique=True, blank=False)
    fullname = models.CharField(max_length=80, blank=False)
    birthday = models.DateField(blank=False)
    SEX_CHOICES = (
        ('M', '남자'),
        ('F', '여자'),
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=False)
    tagline = models.CharField(max_length=512, blank=True, null=True)
    # photo = models.ImageField(upload_to='user/%Y/%m/%d', blank=True, null=True)
    photo = ProcessedImageField(upload_to='user/%Y/%m/%d', blank=True, null=True,
                                processors=[ResizeToFill(120, 120, Anchor.TOP)],
                                format='JPEG',
                                options={'quality': 100})
    school = models.ForeignKey(School, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    updated_on = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_on = models.DateTimeField(null=True, blank=True)

    target_from = models.DateField(null=True, blank=True)
    target_to = models.DateField(null=True, blank=True)
    target_books = models.SmallIntegerField(null=True)

    friends_by_me = models.ManyToManyField('self', through='Friendship',
                                           symmetrical=False,
                                           related_name='friends_by_others',
                                           through_fields=('inviter', 'invitee'))
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'ful`lname', 'birthday', 'sex']

    def update_last_login(self):
        self.last_login_on = timezone.now()
        self.save()

    def search(self, query):
        users = User.objects.filter(Q(username__contains=query) | Q(fullname__contains=query))

        # Exclude self from search_list
        friends = self.get_friends()
        friends_id_list = [self.id]
        if friends and len(friends) > 0:
            friends_id_list.extend(friends.values_list('id', flat=True).order_by('id'))

        return users.exclude(id__in=friends_id_list).all().order_by('fullname')

    def get_all_friends_notes(self):
        """
            현재 사용자와 친구들의 노트 목록을 리턴한다.
        """
        friends = self.get_friends()
        notes = BookNote.objects.filter(Q(user__in=friends, share_to__in=['F', 'P']) | Q(user=self))

        return notes.order_by('-updated_on')

    def get_my_notes(self):
        """
            현재 사용자의 노트 목록을 리턴한다.
        """
        return self.booknotes.order_by('-updated_on')

    def add_friend(self, friend):
        friendship = Friendship(inviter=self, invitee=friend)
        if friendship:
            friendship.save()
        return friendship

    def remove_friend(self, friend):
        friendship = Friendship.objects.get(inviter=self, invitee=friend)
        if friendship:
            friendship.delete()
        return friendship

    def approve_friend(self, friend):
        friendships = Friendship.objects.filter(inviter=friend, invitee=self)
        if len(friendships) == 1:
            friendships[0].status = 'A'
            friendships[0].save()
            return friendships[0]

    def reject_friend(self, friend):
        friendships = Friendship.objects.filter(inviter=friend, invitee=self)
        if len(friendships) == 1:
            friendships[0].status = 'R'
            friendships[0].save()
            return friendships[0]

    def get_friends(self):
        confirmed_friends = self.friends_by_others.filter(friendship_by_me__status='A') | \
                            self.friends_by_me.filter(friendship_by_others__status='A')
        return confirmed_friends.distinct().order_by('fullname')

    def get_friends_by_me(self):
        return self.friends_by_me.filter(friendship_by_others__status='N')

    def get_friends_by_others(self):
        return self.friends_by_others.filter(friendship_by_me__status='N')

    @property
    def get_recommended_friends(self):
        # Get the friend list that my friends knows.
        my_friends = self.get_friends()

        my_friends_id_list = list(my_friends.values_list('id', flat=True))

        friends = User.objects.filter(Q(friends_by_me__id__in=my_friends_id_list) |
                                      Q(friends_by_others__id__in=my_friends_id_list)) \
            .exclude(Q(id=self.id) | Q(id__in=my_friends_id_list)) \
            .annotate(cnt=Count('username'))

        if friends.count() > 10:
            return friends.order_by('-cnt')

        potential_friends_id_list = friends.values_list('id', flat=True)

        # Get the friends based on the same school
        friends_with_same_school = User.objects.filter(school=self.school) \
            .exclude(Q(id=self.id) |
                     Q(id__in=my_friends_id_list) |
                     Q(id__in=potential_friends_id_list)).order_by('-fullname').annotate(cnt=0)

        friends = (friends | friends_with_same_school).order_by('+fullname').order_by('-cnt')

        return friends

    def is_target_set(self):
        return self.target_from and self.target_to and self.target_books and self.target_books > 0

    def get_note_stat(self):
        all_count = self.booknotes.count()
        week_count = self.booknotes.filter(created_at__range=get_this_week_range()).count()
        if self.is_target_set():
            target_count = self.booknotes.filter(created_at__range=(self.target_from, self.target_to)).count()
        else:
            target_count = 0

        return {'total_count': all_count, 'week_count': week_count, 'target_count': target_count,
                'target_max': self.target_books}

    def get_friends_count(self):
        friends_count = self.get_friends().count()
        friends_by_others_count = self.get_friends_by_others().count()

        return {'friends': friends_count, 'friends_by_others': friends_by_others_count}

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.fullname

    def get_short_name(self):
        return self.fullname

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'users'


class Friendship(models.Model):
    inviter = ForeignKey(User, related_name='friendship_by_me')
    invitee = ForeignKey(User, related_name='friendship_by_others')

    STATUS_CHOICES = (
        ('N', '요청'),
        ('A', '승락'),
        ('R', '거절'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N', blank=False)
    updated_on = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_to_friends(user):
        friend_relations = Friendship.objects.filter(to_user=user, status='N')
        return list(map(lambda x: x.from_user, friend_relations))

    @staticmethod
    def get_from_friends(user):
        friend_relations = Friendship.objects.filter(from_user=user, status='N')
        return list(map(lambda x: x.to_user, friend_relations))

    @staticmethod
    def get_confirmed_friends(user):
        friend_relations = Friendship.objects.filter(Q(from_user=user) | Q(to_user=user), status='Y')
        return list(map(lambda x: x.from_user, friend_relations))

    @staticmethod
    def confirm_friend(user, friend):
        relation = Friendship.objects.get(to_user=user, from_user=friend)
        if relation:
            relation.status = 'Y'
            relation.save()
        return relation

    @staticmethod
    def reject_friend(user, friend):
        relation = Friendship.objects.get(to_user=user, from_user=friend)
        if relation:
            relation.status = 'N'
            relation.save()
        return relation

    def __str__(self):
        return self.inviter.username + " - " + self.invitee.username

    class Meta:
        db_table = 'friendships'
        unique_together = ('inviter', 'invitee')


class BookCategory(models.Model):
    name = CharField(max_length=50, blank=False)

    updated_on = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'book_categories'


class Book(models.Model):
    title = CharField(max_length=128, blank=False)
    category = CharField(max_length=128, blank=True)
    isbn = CharField(max_length=10, blank=True, unique=False)
    barcode = models.CharField(max_length=16, blank=True)
    author = CharField(max_length=128, blank=False)
    isbn13 = CharField(max_length=13, blank=True, unique=False)
    author_etc = CharField(max_length=128, blank=True)
    illustrator = CharField(max_length=128, blank=True)
    translator = CharField(max_length=50, blank=True)
    publisher = CharField(max_length=128, blank=True)
    pub_date = DateField(blank=True, null=True)
    description = TextField(blank=True)
    photo = models.URLField(blank=True)
    link = models.URLField(blank=True)
    updated_on = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)
    # age_level = models.PositiveIntegerField(null=False, default=1048575)
    age_level = models.PositiveIntegerField(null=False, default=0)

    @staticmethod
    def get_recommended_books(user):
        age_level = convert_birthday_to_age_level(user.birthday)
        where_clause = "age_level & {0} = {1}".format(age_level, age_level)
        books = Book.objects.extra(where=[where_clause]).exclude(booknotes__user=user).annotate(
            num_notes=Count('booknotes'), avg_rating=Avg('booknotes__rating')).order_by('-num_notes',
                                                                                        '-avg_rating',
                                                                                        '-pub_date')
        return books

    @staticmethod
    def get_book_with_rating(pk):
        try:
            book = Book.objects.get(pk=pk)
            book_info = book.booknotes.all().aggregate(num_notes=Count('id'), avg_rating=Avg('rating'))
            book.num_notes = book_info.get('num_notes')
            book.avg_rating = book_info.get('avg_rating')

            return book
        except Book.DoesNotExist:
            return None

    def update_age_level_with_user_birthday(self, user):
        age_level = convert_birthday_to_age_level(user.birthday)
        self.age_level = self.age_level | age_level
        self.save()

    @staticmethod
    def get_book_by_isbn(isbn):
        book = None

        len_of_isbn = len(isbn)

        if len_of_isbn == 9:
            book = Book.objects.filter(isbn=isbn).first()
        elif len_of_isbn == 13:
            book = Book.objects.filter(isbn13=isbn).first()

        return book

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'books'


class BookNote(models.Model):
    user = ForeignKey(User, related_name='booknotes')
    book = ForeignKey(Book, related_name='booknotes')

    read_date_from = DateField(null=False)
    read_date_to = DateField(null=False)

    content = TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=False, default=3)
    attach = models.FileField(upload_to=get_file_name, blank=True, null=True)

    SHARE_CHOICES = (
        ('P', '개인'),
        ('F', '친구'),
        ('A', '모두'),
    )

    share_to = CharField(max_length=1, choices=SHARE_CHOICES, blank=False, default='F')
    updated_on = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    @staticmethod
    def get_notes_by_book(book_id):
        return BookNote.objects.filter(book__id=book_id).order_by('-created_at')

    @staticmethod
    def get_notes_by_book_isbn(user, isbn):
        len_of_isbn = len(isbn)

        note = None

        if len_of_isbn == 9:
            note = BookNote.objects.filter(book__isbn=isbn, user=user).first()
        elif len_of_isbn == 13:
            note = BookNote.objects.filter(book__isbn13=isbn, user=user).first()

        return note

    def __str__(self):
        return self.user.fullname + " - " + self.book.title

    class Meta:
        db_table = 'booknotes'
        ordering = ['-created_at']


class BookNoteLikeit(models.Model):
    user = ForeignKey(User, related_name='likeit')
    note = ForeignKey(BookNote, related_name='likeit')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.book.title

    class Meta:
        unique_together = (("user", "note"),)
        db_table = 'booknote_likeit'


class BookNoteReply(models.Model):
    user = ForeignKey(User, related_name='replies')
    note = ForeignKey(BookNote, related_name='replies')

    content = CharField(max_length=258, blank=False)

    updated_on = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    def to_json(self):
        json_obj = {'id': self.id,
                    'user': {'id': self.user.id,
                             'username': self.user.username,
                             'fullname': self.user.fullname},
                    'content': self.content,
                    'created_at': self.created_at,
                    }
        return json_obj

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'booknote_replies'  
