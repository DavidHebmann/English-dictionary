#!/usr/bin/env  python3
#coding=utf-8

from socket import *
import sys
import getpass

def main():
    if len(sys.argv)<3:
        print('argv is error')
        return
    HOST=sys.argv[1]
    PORT=int(sys.argv[2])
    s=socket()
    s.connect((HOST,PORT))


    while True:
        print('''
            =============Welcome============
            -- 1.注册　　2.登录　　 3.退出--
            ================================
            ''')
        try:
            cmd=int(input("请输入选项>>"))
        except Exception:
            print("命令错误！！")
            continue
        if cmd not in [1,2,3]:
            print("没有该选项！！")
            sys.stdin.flush()#清除标准输入
            continue
        elif cmd==1:
            if do_register(s)==0:
                print("注册成功！可以登录")
            else:
                print("注册失败！")
        elif cmd==2:
            name=do_login(s)
            if name!=1:
                print("登录成功！！")
                login(s,name)
            else:
                print("登录失败！！")
        elif cmd==3:
            s.send(b'E')
            sys.exit("谢谢使用")

def do_register(s):
    while True:
        name=input("请输入姓名：")
        passwd1=getpass.getpass("请输入密码：")
        passwd2=getpass.getpass("请再次输入密码：")
        if (' ' in name) or (' ' in passwd1):
            print("用户名或密码不能有空格")
        if passwd1!=passwd2:
            print("两次密码不一致")
            continue
        #将注册信息发送给服务器
        msg='R {} {}'.format(name,passwd1)
        s.send(msg.encode())
        data=s.recv(128).decode()
        if data=='OK':
            return 0
        elif data=='EXISTS':
            print("该用户已存在")
            return 1

def do_login(s):
    name = input("User:")
    passwd = getpass.getpass("Passwd:")
    msg = "L {} {}".format(name,passwd)
    s.send(msg.encode())

    data = s.recv(128).decode()
    if data == 'OK':
        return name
    else: 
        print("用户名或密码不正确")
        return 1 
def do_query(s,name):
    while True:
        word = input('单词:')
        #退出查词
        if word == '##':
            break
        msg = 'Q {} {}'.format(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)
        else:
            print("没有找到该单词")



def do_history(s,name):
    print("历史记录")
    msg='H {}'.format(name)
    s.send(msg.encode())
    data=s.recv(128).decode()
    if data=='OK':
        while True:
            data=s.recv(1024).decode()
            if data=='##':
                break
            print(data)
    else:
        print("没有历史记录")

def login(s,name):
    while True:
        print('''
                =============查询界面============
                -- 1.查词　　2.历史记录　　 3.退出--
                ================================
                ''')
        try:
            cmd=int(input("请输入选项>>"))
        except Exception:
            print("命令错误！！")
            continue
        if cmd not in [1,2,3]:
            print("没有该选项！！")
            sys.stdin.flush()#清除标准输入
            continue
        if cmd==1:
            do_query(s,name)
        elif cmd==2:
            do_history(s,name)
        elif cmd==3:
            return


if __name__=='__main__':
    main()




