""" 更新程序 """

import os
import socket
import threading
import zipfile
from tkinter import messagebox

import tkintertools as tkt

LOGO_PATH = 'Visual Programmer/assets/icon.png'
ADDRESS = ('123.60.101.220', 23333)


class Updater:
    """ 更新器 """

    def __init__(self):  # type: () -> None
        """ 初始化更新界面 """
        self.root = tkt.Tk('Updater', 640, 360, 640, 360)
        self.root.resizable(False, False)
        self.canvas = tkt.Canvas(self.root, 640, 360, 0, 0)
        image = tkt.PhotoImage(LOGO_PATH)
        self.canvas.create_image(320, 120, image=image.zoom(0.4, 0.4, 2))
        self.progressbar = tkt.Progressbar(self.canvas, 70, 240, 500, 30)
        self.description = self.canvas.create_text(320, 300, anchor='center')

    def update_progressbar(self, percentage):  # type: (float) -> None
        """ 更新进度条 """
        self.progressbar.load(percentage)

    def update_description(self, text):  # type: (str) -> None
        """ 更新描述 """
        self.canvas.itemconfigure(self.description, text=text)


class Downloader:
    """ 下载器 """

    def __init__(self, updater):  # type: (Updater) -> None
        """ 初始化连接 """
        self.updater = updater  # 下载器
        threading.Thread(target=self.run, daemon=True).start()

    def _connect(self):  # type: () -> int
        """ 连接服务端，返回文件大小 """
        self.client = socket.socket()  # 套接字
        self.updater.update_description('正在连接服务器')
        self.client.connect(ADDRESS)
        self.updater.update_description('正在验证信息')
        self.client.send('Updater'.encode('utf-8'))  # 验证信息
        self.updater.update_description('正在接收相关数据')
        return int(self.client.recv(1024).decode('utf-8'))

    def _download(self, total_size):  # type: (int) -> None
        """ 下载文件 """
        size = 0  # 已下载文件
        with open('Visual Programmer/download.tmp', 'wb') as download_file:
            while size != total_size:
                package = self.client.recv(4096)
                size += len(package)
                self.updater.update_progressbar(size / total_size)
                download_file.write(package)

    def _unzip(self):  # type: () -> None
        """ 解压文件 """
        with zipfile.ZipFile('Visual Programmer/download.tmp') as download_file:
            download_file.extractall('Visual Programmer')

    def _clean(self):  # type: () -> None
        """ 清理下载文件 """
        os.remove('Visual Programmer/download.tmp')

    def run(self):  # type: () -> None
        """ 更新 """
        try:
            code = 0
            total_size = self._connect()
            self.updater.update_description('正在下载更新文件')
            code = 1
            self._download(total_size)
            self.updater.update_description('正在解压更新文件')
            code = 2
            self._unzip()
            self.updater.update_description('正在清理')
            code = 3
            self._clean()
            self.updater.update_description('更新完成')
            self.updater.root.bell()
        except Exception as exception:
            if code == 0:
                messagebox.showerror('Updater', '服务器连接失败')
            elif code == 1:
                messagebox.showerror('Updater', '下载过程中出现问题')
            elif code == 2:
                messagebox.showerror('Updater', '文件解压失败')
            else:
                messagebox.showwarning('Updater', '未能成功清理冗余文件')
            print('Error: %s' % exception)
            self.updater.root.quit()


if __name__ == '__main__':
    updater = Updater()
    Downloader(updater)
    updater.root.mainloop()
