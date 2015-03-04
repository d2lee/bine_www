# -*- coding: UTF-8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from bine.views import BookList, BookNoteList, BookNoteDetail, \
    BookNoteLikeItUpdate, BookNoteReplyDetail, BookNoteReplyList, IndexView, FriendList, BookDetail, UserView


urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^api/note/$', BookNoteList.as_view()),
    url(r'^api/note/(?P<pk>[0-9]+)/$', BookNoteDetail.as_view()),
    url(r'^api/note/(?P<note_id>[0-9]+)/reply/$', BookNoteReplyList.as_view()),
    url(r'^api/note/(?P<note_id>[0-9]+)/reply/(?P<reply_id>[0-9]+)/$', BookNoteReplyDetail.as_view()),
    url(r'^api/note/(?P<note_id>[0-9]+)/likeit/$', BookNoteLikeItUpdate.as_view()),
    url(r'^api/book/$', BookList.as_view()),
    url(r'^api/book/(?P<pk>[0-9]+)/$', BookDetail.as_view()),
    url(r'^api/book/isbn13/(?P<isbn13>[0-9a-zA-Z]+)/$', BookDetail.as_view()),
    url(r'^api/friend/$', FriendList.as_view()),
    url(r'^api/friend/(?P<pk>[0-9]+)/$', FriendList.as_view()),
    url(r'^api/friend/(?P<action>[a-zA-Z]+)/$', FriendList.as_view()),
    url(r'^api/auth/(?P<username>.*)/$', UserView.as_view()),  # duplication check
    url(r'^api/auth/$', UserView.as_view()),    # register
    url(r'^api/auth/login/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api/auth/refresh_token/$', 'rest_framework_jwt.views.refresh_jwt_token'),
]

urlpatterns = format_suffix_patterns(urlpatterns)