# coding=utf-8

import warnings
import pyautogui
import shutil
import sys
import os
if sys.platform=='win32':
    import win32.win32clipboard as win32clipboard #根据本人现有的一点点能力，只有在Win下才能通过win32clipboard复制除文字外其他内容
    from io import BytesIO #本库用于向Win系统剪贴板复制图片，故只在Win下导入
    from ctypes import *
import pyclip #其他系统仅使用pyclip跨平台方案将文本写入系统剪贴板
import threading #多线程用于同步系统剪贴板
from tkinter import INSERT as TKINSERT #仅使用tk.INSERT
import time #用于在同步剪贴板时添加时间间隔，防止pyclip由于未关闭就打开剪贴板而出错，进而导致Clipboard报错

# 仅在Windows下使用
# 参考 https://xxmdmst.blog.csdn.net/article/details/120631425

class DROPFILES(Structure):
    _fields_ = [
        ("pFiles", c_uint),
        ("x", c_long),
        ("y", c_long),
        ("fNC", c_int),
        ("fWide", c_bool),
    ]

pDropFiles = DROPFILES()
pDropFiles.pFiles = sizeof(DROPFILES)
pDropFiles.fWide = True
matedata = bytes(pDropFiles)

def setClipboardFiles(paths):
    files = ("\0".join(paths)).replace("/", "\\")
    data = files.encode("U16")[2:]+b"\0\0"
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(
            win32clipboard.CF_HDROP, matedata+data)
    finally:
        win32clipboard.CloseClipboard()

def setClipboardFile(file):
    setClipboardFiles([file])

def readClipboardFilePaths():
    win32clipboard.OpenClipboard()
    paths = None
    try:
        return win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
    finally:
        win32clipboard.CloseClipboard()


class Clipboard():
    def __init__(self):
        self.content=None
        self.typelist=['empty','text','file']
        self.nowtype=0
        self.iscopy=False
        sync_sys_t=threading.Thread(target=self.sync_sys_clipboard)
        #sync_sys_t.start()
    def set(self,content,typestr):
        if typestr in self.typelist:
            self.content=content
            self.nowtype=self.typelist.index(typestr)
        else:
            warnings.warn("Clipboard type error in Clipboard.set()\nContent has not been changed. Type '"+typestr+
                          "'is not in type list. Clipboard content type must be one of "+str(self.typelist))
    def get(self):
        return self.content,self.typelist[self.nowtype]
    def getcontent(self):
        return self.content
    def gettype(self):
        return self.typelist[self.nowtype]
    def gettypeno(self):
        return self.nowtype
    def clear(self):
        self.content=None
        self.nowtype=0
    def set_sys_clipboard(self,content,typeno):
        if sys.platform!='win32':
            if typeno==1:
                pyclip.copy(self.content)
            else:
                print('Can only copy text to system clipboard on non-Windows platforms. (Sorry 4 that :(')
        else:
            match typeno:
                case 0:
                    warnings.warn('Argument error in Clipboard.set_sys_clipboard()\n Nothing to copy to system clipboard. '+
                                  'typeno argument must not be 0, which means that the clipboard is empty.')
                case 1:
                    pyclip.copy(str(self.content).encode('utf-8'))
                case 2:
                    setClipboardFile(self.content)
    def sync_sys_clipboard(self):
        while True:
            try:
                sys_clipboard_content=pyclip.paste().decode('utf-8')
                if sys_clipboard_content!=self.content:
                    self.iscopy=True
                    self.set(sys_clipboard_content,'text')
                time.sleep(0.3)
            except Exception as e:
                #print('Bad content type in system clipboard from Clipboard.sync_sys_clipboard.   '+str(e))
                pass
                #break
    def copy(self,content,typestr):
        self.clear()
        self.iscopy=True
        self.set(content,typestr)
        self.set_sys_clipboard(content,self.typelist.index(typestr))
    def cut(self,content,typestr):
        self.clear()
        self.iscopy=False
        self.set(content,typestr)
        self.set_sys_clipboard(content,self.typelist.index(typestr))
    def paste(self,towhere,tkinsert=False):
        match self.nowtype:
            case 0:
                print('Nothing to paste')
            case 1:
                if tkinsert:
                    towhere.insert(TKINSERT,str(self.content))
                else:
                    pyautogui.typewrite(str(self.content))
            case 2:
                shutil.copyfile(str(self.content),towhere)
            case _:
                warnings.warn("Clipboard type error in Clipboard.paste()\nContent has not been pasted. Type no. '"+self.nowttpe+
                          "'is not in type list. Clipboard content type no. must be less than "+str(len(self.typelist)-1))
    def paste_at_file(self,towhere):
        if self.nowtype==2:
            if self.iscopy:
                shutil.copy(self.content,towhere)
            else:
                shutil.move(self.content,towhere)
                
