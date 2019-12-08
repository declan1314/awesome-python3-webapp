import sqlite3
conn = sqlite3.connect('test.db') # 建立连接，如果不存在将会创建
print ("Open database successfully")
cursor = conn.cursor() # 创建cursor
cursor.execute("CREATE TABLE COMPANY(ID INT PRIMARY KEY NOT NULL,"
               "NAME TEXT NOT NULL,AGE INT NOT NULL,ADDRESS CHAR(50),SALARY REAL);")
cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (1, 'Paul', 32, 'California', 20000.00 );")

cursor.execute("INSERT INTO COMPANY VALUES (2, 'Allen', 25, 'Texas', 15000.00 );")
cursor.execute("INSERT INTO COMPANY VALUES (3, 'Teddy', 23, 'Norway', 20000.00 );")
cursor.execute("INSERT INTO COMPANY VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 );")
cursor.execute("INSERT INTO COMPANY VALUES (5, 'David', 27, 'Texas', 85000.00 );")
cursor.execute("INSERT INTO COMPANY VALUES (6, 'Kim', 22, 'South-Hall', 45000.00 );")
cursor.execute("INSERT INTO COMPANY VALUES (7, 'James', 24, 'Houston', 10000.00 );")
cursor.execute("SELECT * FROM COMPANY;")

results = cursor.fetchall()
for row in results:
    print(row)

cursor.close() # 关闭cursor
conn.commit() # 提交事务
conn.close() # 关闭连接