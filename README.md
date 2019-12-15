运维系统
======================
###安装运行环境
yum install python3 -y

####安装依赖
pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

####初始化数据库
python3 init_db.py
####启动项目
nohup python3 www/app.py &

###管理员默认账号密码
admin@qq.com/admin123

###关闭项目
ps -ef | grep 'python3 www/app.py' | awk '{print $2}' | xargs kill -9