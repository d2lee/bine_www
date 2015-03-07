# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import bine.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(max_length=40, unique=True)),
                ('email', models.EmailField(max_length=75, unique=True)),
                ('fullname', models.CharField(max_length=80)),
                ('birthday', models.DateField()),
                ('sex', models.CharField(max_length=1, choices=[('M', '남자'), ('F', '여자')])),
                ('tagline', models.CharField(max_length=128, blank=True)),
                ('photo', models.ImageField(blank=True, upload_to='authentication/%Y/%m/%d')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_login_on', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'users',
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=128)),
                ('category', models.CharField(max_length=128, blank=True)),
                ('isbn', models.CharField(max_length=10, blank=True)),
                ('barcode', models.CharField(max_length=16)),
                ('author', models.CharField(max_length=128)),
                ('isbn13', models.CharField(max_length=13, unique=True)),
                ('author_etc', models.CharField(max_length=128, blank=True)),
                ('illustrator', models.CharField(max_length=128, blank=True)),
                ('translator', models.CharField(max_length=50, blank=True)),
                ('publisher', models.CharField(max_length=128, blank=True)),
                ('pub_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('photo', models.URLField(blank=True)),
                ('link', models.URLField(blank=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'books',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'book_categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookNote',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('read_date_from', models.DateField()),
                ('read_date_to', models.DateField()),
                ('content', models.TextField(blank=True)),
                ('preference', models.CharField(max_length=1, default=3)),
                ('attach', models.ImageField(upload_to=bine.models.get_file_name, blank=True, null=True)),
                ('share_to', models.CharField(max_length=1, choices=[('P', '개인'), ('F', '친구'), ('A', '모두')], default='F')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(related_name='booknotes', to='bine.Book')),
                ('user', models.ForeignKey(related_name='booknotes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'booknotes',
                'ordering': ['-created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookNoteLikeit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.ForeignKey(related_name='likeit', to='bine.BookNote')),
                ('user', models.ForeignKey(related_name='likeit', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'booknote_likeit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookNoteReply',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('content', models.CharField(max_length=258)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.ForeignKey(related_name='replies', to='bine.BookNote')),
                ('user', models.ForeignKey(related_name='replies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'booknote_replies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('status', models.CharField(max_length=1, choices=[('N', '요청'), ('A', '승락'), ('R', '거절')], default='N')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invitee', models.ForeignKey(related_name='friendship_by_others', to=settings.AUTH_USER_MODEL)),
                ('inviter', models.ForeignKey(related_name='friendship_by_me', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'friendships',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together=set([('inviter', 'invitee')]),
        ),
        migrations.AlterUniqueTogether(
            name='booknotelikeit',
            unique_together=set([('user', 'note')]),
        ),
        migrations.AddField(
            model_name='user',
            name='friends_by_me',
            field=models.ManyToManyField(related_name='friends_by_others', to=settings.AUTH_USER_MODEL, through='bine.Friendship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', verbose_name='user permissions', help_text='Specific permissions for this user.', blank=True),
            preserve_default=True,
        ),
    ]
