#!/usr/bin/env  python3
#coding=utf-8


'''
name:David
date:2018-7-27
email:zhangxiaoming7875@163.com
modules:python3.5  pymysql
This is a dict project for AID class
'''
from socket import *
import os
import signal
import time
import pymysql
import sys


DICT_TEXT='./dict.txt'
HOST='127.0.0.1'
PORT=8000
ADDR=(HOST,PORT)

#主控制流程
def main():
    #数据库连接
    db=pymysql.connect('localhost','root','123456','dict')
    #创建套接字
    s=socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    #忽略子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr=s.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue
        #创建子进程
        pid=os.fork()
        if pid<0:
            print("create process failed")
            c.close()
        elif pid==0:
            s.close()
            do_child(c,db)
        else:
            c.close()
def do_child(c,db):
    #循环接收客户请求
    while True:
        data = c.recv(128).decode()
        print("Request:",data)

        if data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            name = do_login(c,db,data)
        elif data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_history(c,db,data)

def do_register(c,db,data):
    print("注册操作")
    l=data.split()
    name=l[1]
    passwd=l[2]
    cursor=db.cursor()#新建游标
    #判断姓名是否存在
    sql = "select name from user where name='%s'"%name
    cursor.execute(sql)
    r=cursor.fetchone()
    if r!=None:
        c.send(b'EXISTS')
        return 
    #插入到user数据库
    sql = "insert into user (name,passwd) values ('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        c.send(b'FAIL')
        db.rollback()
        return
    else:
        print("%s注册成功"%name)
def do_login(c,db,data):
    print("登录操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s' and passwd='%s'"%(name,passwd)
    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        c.send(b"FALL")
    else:
        c.send(b'OK')
        return name  

def do_query(c,db,data):
    print("查询操作")
    l=data.split()
    name = l[1]
    word = l[2]
    cursor = db.cursor()


    def insert_history():
        tm = time.ctime()
        sql = "insert into hist (name,word,time) \
        values ('%s','%s','%s')"%(name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            return

    #使用数据库查询
    sql = "select * from words where word='%s'"%word
    try:
        cursor.execute(sql)
        r = cursor.fetchone()
    except:
        pass 

    if not r:
        c.send(b'FALL')
    else:
        c.send(b'OK')
        time.sleep(0.1)
        msg = "{} 　:　 {}".format(r[1],r[2])
        c.send(msg.encode())
        insert_history()

def do_history(c,db,data):
    print("历史记录")
    name=data.split()[1]
    cursor=db.cursor()
    try:
        sql="select * from hist where name='%s'"%name
        print(sql)
        cursor.execute(sql)
        r=cursor.fetchall()
        if not r:
            c.send(b'FAIL')
            return 
        else:
            c.send(b'OK')
    except:
        c.send(b'FAIL')
    for i in r:
        time.sleep(0.1)
        msg="%s %s %s"%(i[1],i[2],i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b"##")


if __name__=='__main__':
    main()



