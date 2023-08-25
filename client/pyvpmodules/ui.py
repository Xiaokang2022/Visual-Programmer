import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filebox
from tkinter import *
import os
import sys
import pyautogui
import time
import threading

currcwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])

class FileTree():
    # path = r"E:\\python开发工具\\project\\tkinter"
    path = os.path.abspath(".")
    file_types = [".png", ".jpg", ".jpeg", ".ico", ".gif"]
    scroll_visiblity = True
    
    font = 11
    font_type = "Courier New"
    
    def __init__(self,parent,selcommand=lambda item:print('已选择项目 '+str(item))):
        currcwd=os.getcwd()
        os.chdir(os.path.split(os.path.realpath(__file__))[0])

        self.root=None
        
        # 左侧frame
        self.left_frame = Frame(parent)
        
        self.tree = ttk.Treeview(self.left_frame, show = "tree", selectmode = "browse")
        tree_y_scroll_bar = Scrollbar(self.left_frame, command = self.tree.yview, relief = SUNKEN, width = 2)
        tree_y_scroll_bar.pack(side = RIGHT, fill = Y)
        self.tree.config(yscrollcommand = tree_y_scroll_bar.set)
        self.tree.pack(expand = 1, fill = BOTH)
        # 设置文件图标
        self.folder_img = PhotoImage(file = r"../img/fileicon/folder.png")
        self.file_img = PhotoImage(file = r"../img/fileicon/text_file.png")
        
        php_img = PhotoImage(file = r"../img/fileicon/php.png")
        python_img = PhotoImage(file = r"../img/fileicon/python.png")
        image_img = PhotoImage(file = r"../img/fileicon/img.png")

        self.icon = {".php": php_img, ".py": python_img, ".pyc": python_img, ".png": image_img, ".jpg": image_img, ".jpeg": image_img, ".gif": image_img, ".ico": image_img}
        
        # 加载目录文件
        self.load_tree("", self.path)
        self.selcmd=selcommand
        self.tree.bind("<<TreeviewSelect>>", lambda event:self.selcmd(self.tree.item(self.tree.focus())))

        os.chdir(currcwd)

        self.sync_t=threading.Thread(target=self.auto_refresh)
    def delete_tree(self):
        self.tree.delete(self.tree.get_children())
    ''' 设置默认搜索路径'''
    def open_dir(self,fileboxtitle='设置目录'):
        path = filebox.askdirectory(title = fileboxtitle, initialdir = self.path)
        print("设置路径："+path)
        self.path = path
        # 删除所有目录
        self.delete_tree()
        self.load_tree("", self.path)
        return path
    ''' 获取文件后缀'''
    def file_extension(self, file):
        file_info = os.path.splitext(file)
        return file_info[-1]
    ''' 获取目录名称'''
    def dir_name(self, path):
        path_list = os.path.split(path)
        return path_list[-1]
    ''' 加载目录'''
    def load_tree(self, root, path, opened=[]):
        is_open = False
        #print(path,opened)
        isrootdir=False
        if root == "" or (path in opened):
            is_open = True
            isrootdir=True
        root = self.tree.insert(root, END, text = " " + self.dir_name(path), values = (path,), open = is_open, image = self.folder_img)
        if isrootdir:
            print('Reading root dir, reroot.')
            self.root=root
        try:
            for file in os.listdir(path):
                file_path = path + "/" + file
                if os.path.isdir(file_path):
                    self.load_tree(root, file_path,opened=opened)
                else:
                    ext = self.file_extension(file)
                    img = self.icon.get(ext)
                    if img is None:
                        img = self.file_img
                    self.tree.insert(root, END, text = " " + file, values = (file_path,), image = img)
        except Exception as e:
            print(e)
    '''获取当前焦点目录'''
    def get_focus_dir(self):
        sel=self.tree.item(self.tree.selection())['values'][0]
        if os.path.isdir(sel):
            return sel
        else:
            return os.path.split(sel)[0]
    '''获取展开项'''
    def get_opened(self,parent=None,last_res=[]):
        if parent==None:
            print(self.root)
            children=self.tree.get_children(self.root)
        else:
            children=self.tree.get_children(parent)
        print(children)
        for item in children:
            if bool(self.tree.item(item)['open']):
                last_res.append(self.tree.item(item)['values'][0])
                self.get_opened(parent=item)
        print(last_res)
        return last_res
    '''刷新'''
    def refresh(self):
        opened=self.get_opened()
        selpath=self.tree.item(self.tree.focus())['values'][0]
        self.delete_tree()
        self.load_tree('',self.path,opened=opened)
        self.tree.unbind("<<TreeviewSelect>>")
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0]==selpath:
                print('focused on: '+str(self.tree.item(item)['values'][0]))
                self.tree.focus(item=item)
        self.tree.bind("<<TreeviewSelect>>", lambda event:self.selcmd(self.tree.item(self.tree.focus())))
    '''自动刷新（必须在多线程中使用）'''
    def auto_refresh(self):
        path_to_watch = self.path
        before = []
        for f in os.scandir(path_to_watch):
            before.append(f.path)
        while True:
            time.sleep (2)
            after = []
            for f in os.scandir(path_to_watch):
                after.append(f.path)
            #print(before)
            #print(after)
            if after!=before:
                print('New/Deleted file in dir, retree')
                self.refresh()
            before = after

class Menu(tk.Toplevel):
    '''
    是个tttk的好苗子，等到这玩意加进tttk后就有可供参考的内容了
    唯一需要注意的是，content即菜单内容中不能有文字重复项，否则可能会有bug
    content的格式与tttk.BtnRow大同小异，可以到tttk文档或readme中查看
    pos，为相对于屏幕左上角的坐标元组或'cur'表示鼠标位置
    '''
    def __init__(self,parent,content,pos='cur',width=100,bg='#ffffff',fg='#000000',selbg='#cccccc',selfg='#000000',
                 showcanclebtn=True,cancletxt='取消',canclefg='#cc0000',cancleselfg='#cc0000'):
        tk.Toplevel.__init__(self)
        self.title('Menu')
        self.overrideredirect(True)
        self.transient(parent)
        self.wm_attributes('-topmost',True)
        self.content=content
        self.pos=pos
        self.width=width
        self.btns=[]
        for i in list(content.keys()):
            self.btns.append(tk.Button(self,text=i,command=lambda lambda_i=i:self.do(self.content[lambda_i]),bg=bg,fg=fg,bd=0,anchor='w'))
        for btn in self.btns:
            btn.pack(fill=tk.X)
            btn.bind('<Enter>',lambda event,lambda_btn=btn:self.setcolor(lambda_btn,selbg,selfg))
            btn.bind('<Leave>',lambda event,lambda_btn=btn:self.setcolor(lambda_btn,bg,fg))
        if showcanclebtn:
            canclebtn=tk.Button(self,text=cancletxt,command=self.hide,bg=bg,fg=canclefg,bd=0,anchor='w')
            canclebtn.pack(fill=tk.X)
            canclebtn.bind('<Enter>',lambda event,lambda_btn=canclebtn:self.setcolor(lambda_btn,selbg,cancleselfg))
            canclebtn.bind('<Leave>',lambda event,lambda_btn=canclebtn:self.setcolor(lambda_btn,bg,canclefg))
        self.update()
        self.geometry(str(self.width)+'x'+str(self.winfo_height()))
        self.withdraw()
    def setcolor(self,btn,newbg,newfg):
        btn['bg']=newbg
        btn['fg']=newfg
    def getpos(self):
        if self.pos=='cur':
            return (pyautogui.position()[0]+10,pyautogui.position()[1]+10)
        else:
            return self.pos
    def show(self):
        self.deiconify()
        newx,newy=self.getpos()
        self.geometry(str(self.width)+'x'+str(self.winfo_height())+'+'+str(newx+10)+'+'+str(newy+10))
    def _hide(self):
        self.withdraw()
    def hide(self):
        for i in range(0,5):
            self.wm_attributes('-alpha',1-0.2*i)
            self.update()
            time.sleep(0.02)
        self._hide()
        self.wm_attributes('-alpha',1)
    def do(self,func):
        self.hide()
        func()

os.chdir(currcwd)
