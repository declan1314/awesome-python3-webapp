运维系统
======================
###安装运行环境
yum install python3 -y
####初始化数据库
python3 init_db.py

####安装依赖
pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
####启动项目
python3 www/app.py

###管理员默认账号密码
admin/123456