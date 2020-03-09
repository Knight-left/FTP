"""
    ftp  文件服务器
    并发网络功能训练

"""

from socket import *
from threading import Thread
import sys,os
from time import sleep


# 全局变量
HOST = "0.0.0.0"  # IP地址
PORT = 8080  # 端口
ADDR = (HOST, PORT)  # 服务端地址
FTP = "/home/tarena/FTP/"   # 文件库路径

# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self,c,ftp_path):
        self.c = c
        self.ftp_path = ftp_path
    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.ftp_path)
        if not files:
            self.c.send("该文件列表为空".encode())
            return
        # TCP粘包问题,连续把这四个都发送完了
        # 那边一次性接收,肯定接收的就不是OK了
        # 可以每次发送之后,sleep(0.1)
        # 但是sleep多了就费时间,可以一次或两次
        # 也可以人为添加消息边界(比如换行字符'\n')!!
        else:
            self.c.send(b'OK')
            sleep(0.1)

        # 这样就是这边一次性发送,那边一次性接收
        # 不会出现粘包问题
        # '\n'就是消息边界(显示换行)(也可以逗号,分号)
        fs = ''
        for file in files:
            if file[0] != '.' and os.path.isfile(self.ftp_path+file):
                fs += file + '\n'
        # 如果出现要发送的东西特别大的情况,那边就循环接收
        # 这边发送完要发送的东西后,sleep(0.1)后发送个
        # 结束标志(例如 ##)
        self.c.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.ftp_path+filename,'rb')
        except Exception:
            self.c.send('文件不存在'.encode())
            return
        else:
            self.c.send(b'OK')
            sleep(0.1)
        # 发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.c.send(b'##')
                break
            self.c.send(data)

    def do_put(self,filename):
        if os.path.exists(self.ftp_path + filename):
            self.c.send("该文件已经存在".encode())
            return
        self.c.send(b'OK')
        fd = open(self.ftp_path+filename,'wb')
        # 发送文件内容
        while True:
            data = self.c.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()

# 客户端请求处理函数
def handle(c):
    # 选择文件目录
    cls = c.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'
    ftp = FtpServer(c,FTP_PATH)
    while True:
        # 接收客户端请求
        data = c.recv(1024).decode()
        # 为保证风格统一,这里写成data[0]
        # 这里的not data主要是处理客户端崩溃退出的情况
        # 比如客户端按Ctrl+F2,这里会接收到空
        # return是因为,如果handle函数结束,线程自动结束
        if not data or data[0] == 'Q':
            return   # 结束handle函数
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)

# 网络搭建
def main():
    s = socket()  # 创建tcp套接字
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 端口立马重用
    s.bind(ADDR)
    s.listen(5)
    print("Listen the port 8080...")
    # 循环等待客户端连接
    while True:
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue  # 捕获到其它异常,继续执行等待连接
        print("连接的客户端:",addr)

        # 创建线程处理请求
        client = Thread(target=handle,args=(c,))
        client.setDaemon(True)
        client.start()

if __name__ == "__main__":
    main()





