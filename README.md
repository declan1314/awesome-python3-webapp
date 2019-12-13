运维系统
======================
###安装运行环境
yum install
####初始化数据库
python www/init_db.py

####安装依赖
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
####启动项目
python www/app.py