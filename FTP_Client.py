from socket import *
import sys
from time import sleep

# 具体功能封装为类
class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L') # 发送请求(自己定协议)
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # ok表示请求成功
        if data == 'OK':
            # 接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用") # 进程结束,客户端退出

    # 从某个文件里读,写到当前目录下的文件里,就叫下载
    # 尽量以二进制方式读写,因为可能是各种类型的文件
    def do_get(self,filename):
        # 发送请求
        self.sockfd.send(('G '+filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            fd = open(filename,'wb')
            # 接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self,filename):
        try:
            fd = open(filename, 'rb')
        except Exception:
            print("没有该文件")
            return

        # 获取真正文件名字(对某个路径的文件的切割解析)
        filename = filename.split('/')[-1]
        # 发送请求
        self.sockfd.send(('P '+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)
# 发起请求
def request(sockfd):
    # 当一个类中的所有方法都用到这个参数时
    # 就可以把这个参数变成类里的属性
    ftp = FtpClient(sockfd)

    while True:
        print("\n========命令选项==========")
        print("********* list **********")
        print("******* get file ********")
        print("******* put file ********")
        print("******** quit ***********")
        print("=========================")

        cmd = input("输入命令:")
        if cmd == 'list':
            ftp.do_list()
        elif cmd == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1] # -1和1一样
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)

# 网络连接
def main():
    ADDR = ('127.0.0.1',8080)
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception:
        print("连接服务器失败")
        return
    else:
        print("""
                ********************
                    Data   File
                ********************
        """)
        cls = input("请输入想要的文件类别:")
        if cls not in ['Data','File']:
            print("Sorry input Error!!")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)   # 发送具体请求


if __name__ == "__main__":
    main()


