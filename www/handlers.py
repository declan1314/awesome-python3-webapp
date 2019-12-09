#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

from collections import namedtuple

from aiohttp.web_response import Response

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, zipfile

from aiohttp import web

from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError, APIError

from models import User, next_id, AppServer, RootPath, DownloadLog
from config import configs
import paramiko

import os

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def check_auth(request):
    if request.__user__ is None:
        raise APIPermissionError('Please signin first.')


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        # user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/register')
def register(request):
    check_admin(request)
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@post('/api/authenticate')
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }


@get('/manage/logs')
def manage_logs(*, page='1'):
    return {
        '__template__': 'manage_logs.html',
        'page_index': get_page_index(page)
    }


@get('/api/logs')
def api_get_logs(request, *, page='1'):
    check_admin(request)
    page_index = get_page_index(page)
    num = yield from DownloadLog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    download_logs = yield from DownloadLog.findAll(orderBy='created_date desc', limit=(p.offset, p.limit))
    return dict(page=p, download_logs=[download_log._asdict() for download_log in download_logs])


@get('/api/users')
def api_get_users(request, *, page='1'):
    check_admin(request)
    page_index = get_page_index(page)
    num = yield from User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.findAll(orderBy='created_date desc', limit=(p.offset, p.limit))
    # for u in users:
    #     u.passwd = '******'
    return dict(page=p, users=[user._asdict() for user in users])


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
def api_register_user(request, *, email, name, passwd):
    check_admin(request)

    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    # user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/')
def main_page(*, page='1'):
    return 'redirect:/api/servers'


@get('/api/servers')
def api_servers(request, *, page='1'):
    check_auth(request)

    page_index = get_page_index(page)
    num = yield from AppServer.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
        app_servers = []
    else:
        app_servers = yield from AppServer.findAll(orderBy='created_date desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'app_servers.html',
        'page': page,
        'servers': app_servers
    }


@get('/api/servers/{id}/paths')
def api_paths(request, *, id, page=1):
    check_auth(request)
    page_index = get_page_index(page)
    num = yield from RootPath.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
        root_paths = []
    else:
        root_paths = yield from RootPath.findAll(orderBy='created_date desc', where='app_server_id = ' + id,
                                                 limit=(page.offset, page.limit))
    back_url = '/api/servers'

    app_server = yield from AppServer.find(id)

    return {
        '__template__': 'root_paths.html',
        'page': page,
        'paths': root_paths,
        'server_id': id,
        'back_url': back_url,
        'server': app_server
    }


@get('/api/servers/{server_id}/paths/{path_id}')
def api_root_path(request, *, server_id, path_id):
    return get_path(request, server_id, path_id)


@get('/api/servers/{server_id}/paths/{path_id}/path/{path}')
def api_path(request, *, server_id, path_id, path):
    return get_path(request, server_id, path_id, path)


def get_path(request, server_id, path_id, path=''):
    check_auth(request)
    app_server = yield from AppServer.find(server_id)
    root_path = yield from RootPath.find(path_id)
    f_list = get_folders_and_files(hostname=app_server.host, port=app_server.ssh_port,
                                   username=app_server.username,
                                   password=app_server.password, root_path=root_path.path, relative_path=path)

    back_url = '/api/servers/' + server_id + '/paths' + ('/' + path_id if not len(path) == 0 else '') + (
        '/path' + path[:path.rfind('/')] if not len(path) == 0 and path.rfind('/') != -1 else '')
    return {
        '__template__': 'root_path.html',
        'f_list': f_list,
        'back_url': back_url,
        'path': root_path,
        'server': app_server
    }


@get('/api/servers/{server_id}/paths/{path_id}/path/{path}/download')
def api_download(request, *, server_id, path_id, path):
    app_server = yield from AppServer.find(server_id)
    root_path = yield from RootPath.find(path_id)
    content, filename = download(hostname=app_server.host, port=app_server.ssh_port,
                                 username=app_server.username,
                                 password=app_server.password, root_path=root_path.path, file_path=path)
    response = Response(
        content_type='application/octet-stream',
        headers={'Content-Disposition': 'attachment;filename={}'.format(filename)},
        body=content
    )

    download_log = DownloadLog(id=next_id(), file=root_path.path + '/' + path, server=app_server.host, created_by_name=request.__user__.name,
                               created_by=request.__user__.id, updated_by=request.__user__.id)
    yield from download_log.save()
    return response


def download(hostname, port, username, password, root_path, file_path):
    transport = paramiko.Transport((hostname, port))  # 获取Transport实例
    transport.connect(username=username, password=password)  # 建立连接

    # 创建sftp对象，SFTPClient是定义怎么传输文件、怎么交互文件
    sftp = paramiko.SFTPClient.from_transport(transport)

    # 将服务器 /www/test.py 下载到本地 aaa.py。文件下载并重命名为aaa.py
    abs_file = '/tmp/project' + root_path + '/' + file_path
    abspath = os.path.split(abs_file)[0]
    if not os.path.exists(abspath):
        os.makedirs(abspath)

    sftp.get(root_path + '/' + file_path, abs_file)

    # 关闭连接
    transport.close()

    # zipfile.ZipFile()

    with open(abs_file, 'r', encoding='utf-8') as f:
        return f.read(), os.path.split(abs_file)[1]
    return null, null


def get_folders_and_files(hostname, port, username, password, root_path, relative_path=''):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    try:
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            password=password
        )
    except Exception as e:
        print(e)
        return

    # 设置一个内部函数，执行shell命令并返回输出结果
    def run_shell(cmd):
        ssh_in, ssh_out, ssh_error = ssh.exec_command(cmd)
        result = ssh_out.read() or ssh_error.read()
        return result.decode().strip()

    # 获取指定文件夹中文件的名称，并跟上面得到的文件夹绝对地址组合起来

    relative_path_left = ('/' + relative_path) if not len(relative_path) == 0 else ''
    relative_path_right = (relative_path + '/') if not len(relative_path) == 0 else ''

    cmd_get_sqls = 'cd ' + root_path + relative_path_left + ";ls -alt --ignore='.' --ignore='..' | grep '^d' | awk '{print $9}'"
    sqls = run_shell(cmd_get_sqls)

    f_list = []
    if len(sqls) > 0:
        f_list.extend(
            [{'value': relative_path_right + each, 'type': 'folder', 'name': each} for each in sqls.split('\n')])

    cmd_get_sqls = 'cd ' + root_path + relative_path_left + ";ls -alt | grep '^-' | awk '{print $9}'"
    sqls = run_shell(cmd_get_sqls)
    f_list.extend([{'value': relative_path_right + each, 'type': 'file', 'name': each} for each in sqls.split('\n')])

    # 关闭连接
    ssh.close()
    return f_list
