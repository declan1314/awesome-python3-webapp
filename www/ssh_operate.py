import os
import time
import zipfile

import paramiko


def download_file(hostname, port, username, password, root_path, relative_path):
    timestamp = str(time.time())

    transport = paramiko.Transport((hostname, port))  # 获取Transport实例
    transport.connect(username=username, password=password)  # 建立连接

    # 创建sftp对象，SFTPClient是定义怎么传输文件、怎么交互文件
    sftp = paramiko.SFTPClient.from_transport(transport)

    # 将服务器 /www/init_db.py 下载到本地 aaa.py。文件下载并重命名为aaa.py
    abs_file = '/tmp/project' + root_path + '/' + relative_path
    abspath = os.path.split(abs_file)[0]

    if not os.path.exists(abspath):
        os.makedirs(abspath)

    sftp.get(root_path + '/' + relative_path, abs_file + timestamp)

    # 关闭连接
    transport.close()

    file_path = os.path.split(abs_file)[1]
    file_name, file_type = os.path.splitext(file_path)
    zip_file_name = file_name + ".zip"
    zip_file = abspath + "/" + zip_file_name
    f = zipfile.ZipFile(zip_file + timestamp, 'w', zipfile.ZIP_DEFLATED)
    f.write(abs_file + timestamp, file_path)
    f.close()

    os.remove(abs_file + timestamp)

    with open(zip_file + timestamp, 'rb') as f:
        content = f.read()

    os.remove(zip_file + timestamp)

    return content, zip_file_name


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
    if len(sqls) > 0:
        f_list.extend(
            [{'value': relative_path_right + each, 'type': 'file', 'name': each} for each in sqls.split('\n')])

    # 关闭连接
    ssh.close()
    return f_list
