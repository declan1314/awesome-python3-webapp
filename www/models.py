#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Michael Liao'

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


class AppServer(Model):
    __table__ = 'app_server'

    created_by = IntegerField()
    created_date = FloatField(default=time.time)
    updated_by = IntegerField()
    updated_date = FloatField(default=time.time)
    id = IntegerField(primary_key=True, default=next_id)
    name = StringField(ddl='varchar(16)')
    host = StringField(ddl='varchar(16)')
    username = StringField(ddl='varchar(16)')
    password = StringField(ddl='varchar(32)')
    ssh_port = IntegerField()

class RootPath(Model):
    __table__ = 'root_path'

    created_by = IntegerField()
    created_date = FloatField(default=time.time)
    updated_by = IntegerField()
    updated_date = FloatField(default=time.time)
    id = IntegerField(primary_key=True, default=next_id)
    name = StringField(ddl='varchar(16)')
    path = StringField(ddl='varchar(125)')
    app_server_id = IntegerField()
