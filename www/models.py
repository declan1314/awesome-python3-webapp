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


class DownloadLog(Model):
    __table__ = 'download_log'

    created_by = IntegerField()
    created_date = FloatField(default=time.time)
    updated_by = IntegerField()
    updated_date = FloatField(default=time.time)
    id = IntegerField(primary_key=True, default=next_id)
    name = StringField(ddl='varchar(64)')
    server = StringField(ddl='varchar(64)')
    file = StringField(ddl='varchar(256)')
    created_by_name = StringField(ddl='varchar(64)')
    enable_flag = BooleanField()


class User(Model):
    __table__ = 'users'

    created_by = IntegerField()
    created_date = FloatField(default=time.time)
    updated_by = IntegerField()
    updated_date = FloatField(default=time.time)
    id = IntegerField(primary_key=True, default=next_id)
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')


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
