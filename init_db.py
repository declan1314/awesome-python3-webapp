import sqlite3
conn = sqlite3.connect('app.db')    # 建立连接，如果不存在将会创建
print("Open database successfully")
cursor = conn.cursor()  # 创建cursor
cursor.execute("create table user(created_by varchar(64),created_date real,updated_by varchar(64),updated_date real,"
               "id varchar(64),email varchar(32),passwd varchar(32),admin bool,name varchar(32),image varchar(512),"
               "enable_flag bool);")
cursor.execute("create table app_server(created_by varchar(64),created_date real,updated_by varchar(64),updated_date "
               "real,id varchar(64),name varchar(32),host varchar(16),username varchar(16),password varchar(32),"
               "ssh_port int,enable_flag bool);")
cursor.execute("create table root_path(created_by varchar(64),created_date real,updated_by varchar(64),updated_date "
               "real,id varchar(64),name varchar(32),path varchar(125),app_server_id varchar(64),enable_flag bool);")

cursor.execute("create table download_log (created_by varchar(64),created_date real,updated_by varchar(64),"
               "updated_date real,id varchar(64),name varchar(64),created_by_name varchar(64),server varchar(64),"
               "file varchar(256),enable_flag bool);")
cursor.execute("insert into user values('0015758794996946c7296785da9412fa70ccab8efb59556000',1575879499.69407,"
               "'0015758794996946c7296785da9412fa70ccab8efb59556000',1575879499.69407,"
               "'0015758794996946c7296785da9412fa70ccab8efb59556000','admin@qq.com',"
               "'admin',1,'管理员',"
               "'http://www.gravatar.com/avatar/5a1220e7b9f5d91a4e6c3a0206f2d294?d=mm&s=120',1);")

results = cursor.fetchall()
for row in results:
    print(row)

cursor.close() # 关闭curso
conn.commit() # 提交事务
conn.close() # 关闭连接

print("Init database successfully")