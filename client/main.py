# Python Visual Designer
# 2024 By 小康2022 & 真_人工智障 & CodeCrafter-铁路旁的小学生
# v0.1.2

import tkinter as tk
import tkinter.ttk as ttk
import tkintertools as tkt
import tkinter.messagebox as msgbox
from tkinter import *
import os
import sys
import time
from PIL import ImageTk,Image
import threading
import math
import tkinter.filedialog as filebox
# import pyvpmodules.ui as ui
import pyclip
import pyautogui

os.chdir(os.path.split(os.path.realpath(__file__))[0])
print(os.getcwd())
#os.chdir(sys.argv[0])
global path
path = os.path.abspath(".")
file_types = [".png", ".jpg", ".jpeg", ".ico", ".gif"]
scroll_visiblity = True 

root=tkt.Tk()
root.withdraw()

# 浅做一个启动界面
startwin=tk.Toplevel()
startwin.overrideredirect(True)
startwin.title('Starting PyVP')
startwin.geometry('256x256'+'+'+str((startwin.winfo_screenwidth()-256)//2)+'+'+str((startwin.winfo_screenheight()-256)//2))
icon_pil=Image.open("./icon.png")
icon256_pil=icon_pil.resize((256,256))
icon256_tk=ImageTk.PhotoImage(image=icon256_pil)
tk.Label(startwin,image=icon256_tk,bg='#000000').pack()
startwin.configure(background='#000000')
startwin.wm_attributes('-transparentcolor','#000000')
startwin.wm_attributes('-alpha',0)
# 入场动画
for i in range(0,10):
    startwin.wm_attributes('-alpha',i/10)
    startwin.update()
    time.sleep(0.05)
startwin.update()

#在这里写启动准备工作，时不时记得update()一下防止未响应
#加载界面中一定包含的图片图标等
#左边栏图像
sidebarimgpil=[]
sidebarimg=[]
sidebarimgpil.append(Image.open("./img/sidebar/folder.png"))
sidebarimgpil.append(Image.open("./img/sidebar/code.png"))
sidebarimgpil.append(Image.open("./img/sidebar/function.png"))
sidebarimgpil.append(Image.open("./img/sidebar/class.png"))
sidebarimgpil.append(Image.open("./img/sidebar/modules.png"))

for imgpil in sidebarimgpil:
    sidebarimg.append(ImageTk.PhotoImage(image=imgpil))

#左边栏图像
sidebarbtmimgpil=[]
sidebarbtmimg=[]
sidebarbtmimgpil.append(Image.open("./img/sidebarbtm/more.png"))
sidebarbtmimgpil.append(Image.open("./img/sidebarbtm/run.png"))

for imgpil in sidebarbtmimgpil:
    sidebarbtmimg.append(ImageTk.PhotoImage(image=imgpil))


#准备完成后的拖延时间
for i in range(0,20):
    startwin.update()
    time.sleep(0.1)
#出场动画
for i in range(0,10):
    startwin.wm_attributes('-alpha',1-i/10)
    startwin.update()
    time.sleep(0.05)
startwin.update()
startwin.destroy()

def delete_tree():
    tree.delete(tree.get_children())

''' 设置默认搜索路径'''
def open_dir(patha, fileboxtitle='设置目录'):
    open_path = filebox.askdirectory(title = fileboxtitle, initialdir = patha)
    path = open_path
    # 删除所有目录
    delete_tree()
    load_tree("", path)
    return path

''' 获取文件后缀'''
def file_extension(file):
    file_info = os.path.splitext(file)
    return file_info[-1]

''' 获取目录名称'''
def dir_name(path):
    path_list = os.path.split(path)
    return path_list[-1]

''' 加载目录'''
def load_tree(root, patha, opened=[]):
    is_open = False
    #print(path,opened)
    isrootdir=False
    if root == "" or (patha in opened):
        is_open = True
        isrootdir=True
    root = tree.insert(root, END, text = " " + dir_name(patha), values = (patha,), open = is_open, image = folder_img)
    if isrootdir:
        print('Reading root dir, reroot.')
        root=root
    try:
        for file in os.listdir(patha):
            file_path = patha + "/" + file
            if os.path.isdir(file_path):
                load_tree(root, file_path,opened=opened)
            else:
                ext = file_extension(file)
                img = icon.get(ext)
                if img is None:
                    img = file_img
                tree.insert(root, END, text = " " + file, values = (file_path,), image = img)
    except Exception as e:
        print(e)

'''获取当前焦点目录'''
def get_focus_dir():
    sel=tree.item(tree.selection())['values'][0]
    if os.path.isdir(sel):
        return sel
    else:
        return os.path.split(sel)[0]
    
'''获取展开项'''
def get_opened(parent=None,last_res=[]):
    if parent==None:
        print(root)
        children=tree.get_children(root)
    else:
        children=tree.get_children(parent)
    print(children)
    for item in children:
        if bool(tree.item(item)['open']):
            last_res.append(tree.item(item)['values'][0])
            get_opened(parent=item)
    print(last_res)
    return last_res

'''刷新'''
def refresh():
    opened=get_opened()
    selpath=tree.item(tree.focus())['values'][0]
    delete_tree()
    load_tree('',path,opened=opened)
    tree.unbind("<<TreeviewSelect>>")
    for item in tree.get_children():
        if tree.item(item)['values'][0]==selpath:
            print('focused on: '+str(tree.item(item)['values'][0]))
            tree.focus(item=item)
    tree.bind("<<TreeviewSelect>>", lambda _event:SelectCommand(tree.focus()))

'''自动刷新（必须在多线程中使用）'''
def auto_refresh():
    path_to_watch = path
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
            refresh()
        before = after


font = 11
font_type = "Courier New"

currcwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])

# 左侧frame
left_frame = Frame(root)

# 代码编辑
code_text = Text(root, bg='black', fg='white', font=("JetBrains Mono", 11))

'''在工作区里显示代码或图片等等'''
def SelectCommand(item):
    file_path = tree.item(item)['values'][0]
    if file_path.endswith((".py", ".pyc", ".pyw")):
        pf = open(file_path, encoding="utf-8")
        data = pf.read()
        if code_text.get('1.0', END) == '':
            code_text.insert(END, data)
        else:
            code_text.delete('1.0', END)
            code_text.insert(END, data)

tree = ttk.Treeview(left_frame, show = "tree", selectmode = "browse")
tree_y_scroll_bar = Scrollbar(left_frame, command = tree.yview, relief = SUNKEN, width = 2)
tree_y_scroll_bar.pack(side = RIGHT, fill = Y)
tree.config(yscrollcommand = tree_y_scroll_bar.set)
tree.pack(expand = 1, fill = BOTH)
# 设置文件图标
folder_img = PhotoImage(file = r"./img/fileicon/folder.png")
file_img = PhotoImage(file = r"./img/fileicon/text_file.png")

php_img = PhotoImage(file = r"./img/fileicon/php.png")
python_img = PhotoImage(file = r"./img/fileicon/python.png")
image_img = PhotoImage(file = r"./img/fileicon/img.png")

icon = {".php": php_img, ".py": python_img, ".pyc": python_img, ".png": image_img, ".jpg": image_img, ".jpeg": image_img, ".gif": image_img, ".ico": image_img}

# 加载目录文件
load_tree("", path)
tree.bind("<<TreeviewSelect>>", lambda _event:SelectCommand(tree.focus()))

os.chdir(currcwd)

sync_t=threading.Thread(target=auto_refresh)

class PostMenu(tk.Toplevel):
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
        content=content
        pos=pos
        width=width
        btns=[]
        for i in list(content.keys()):
            btns.append(tk.Button(self,text=i,command=lambda lambda_i=i:self.do(content[lambda_i]),bg=bg,fg=fg,bd=0,anchor='w'))
        for btn in btns:
            btn.pack(fill=tk.X)
            btn.bind('<Enter>',lambda event,lambda_btn=btn:self.setcolor(lambda_btn,selbg,selfg))
            btn.bind('<Leave>',lambda event,lambda_btn=btn:self.setcolor(lambda_btn,bg,fg))
        if showcanclebtn:
            canclebtn=tk.Button(self,text=cancletxt,command=self.hide,bg=bg,fg=canclefg,bd=0,anchor='w')
            canclebtn.pack(fill=tk.X)
            canclebtn.bind('<Enter>',lambda event,lambda_btn=canclebtn:self.setcolor(lambda_btn,selbg,cancleselfg))
            canclebtn.bind('<Leave>',lambda event,lambda_btn=canclebtn:self.setcolor(lambda_btn,bg,canclefg))
        self.update()
        self.geometry(str(width)+'x'+str(self.winfo_height()))
        self.withdraw()
    def setcolor(self,btn,newbg,newfg):
        btn['bg']=newbg
        btn['fg']=newfg
    def getpos(self):
        if self.pos == 'cur':
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

# 类与函数
def resize(parent, #type: tk.Tk | tk.Toplevel | tkt.Tk | tkt.Toplevel
           notframex, #type: int
           notframey  #type: int
           ):
    '''
    parent    Canvas所在的窗口
    notframex Canvas以外的长度（很抽象），就是窗口宽-Canvas宽
    notframey Canvas以外的高度（也很抽象），就是窗口高-Canvas高

    魔改自tkt > __main__.py > Tk() > _zoom()
    '''
    while True:
        width, height = map(int, parent.geometry().split('+')[0].split('x'))
        width-=notframex
        height-=notframey
        # NOTE: 此处必须用 geometry 方法，直接用 Event 或者 winfo 会有画面异常的 bug

        if width != parent.width[1] and height != parent.height[1]:  # 没有大小的改变
            #print('resize canvas to '+'W:'+str(width)+'  '+'H:'+str(height))
            for canvas in parent._canvas:
                if canvas._lock:
                    _resize(canvas,width/canvas.width[1], height/canvas.height[1])

            parent.width[1], parent.height[1] = width, height  # 更新窗口当前的宽高值

def _resize(self,  rate_x=None, rate_y=None):  # type: (float | None, float | None) -> None
    """
    ### 缩放画布及其内部的所有元素
    `rate_x`: 横向缩放比率，默认值表示自动更新缩放（根据窗口缩放程度） \ 
    `rate_y`: 纵向缩放比率，默认值同上
    """
    if not rate_x:
        rate_x = self.master.width[1]/self.master.width[0]/rx
    if not rate_y:
        rate_y = self.master.height[1]/self.master.height[0]/ry
    rate_x_pos, rate_y_pos = rate_x, rate_y  # 避免受 keep 影响
    if self.keep is True:  # 维持比例
        rx = rate_x*self.master.width[1]/self.master.width[0]/rx
        ry = rate_y*self.master.height[1]/self.master.height[0]/ry
        rate_x = rate_y = min(rx, ry)
    # 更新画布的位置及大小的数据
    self.width[1] *= rate_x
    self.height[1] *= rate_y
    temp_x, self.rx = self.rx, self.width[1]/self.width[0]
    temp_y, self.ry = self.ry, self.height[1]/self.height[0]
    place_info = self.place_info()
    tk.Canvas.place(  # 更新画布的位置及大小
        self,
        width=self.width[1],
        height=self.height[1],)
        #x=float(place_info['x'])*rate_x_pos,
        #y=float(place_info['y'])*rate_y_pos)
    for widget in self._widget:  # 更新子画布控件的子虚拟画布控件位置数据
        widget.x1 *= rate_x
        widget.x2 *= rate_x
        widget.y1 *= rate_y
        widget.y2 *= rate_y
    for item in self.find_all():  # item 位置缩放
        self.coords(
            item, *[c*(rate_x, rate_y)[i & 1] for i, c in enumerate(self.coords(item))])
    for item in self._font:  # 字体大小缩放
        self._font[item][1] *= math.sqrt(rate_x*rate_y)
        font = self._font[item][:]
        font[1] = int(font[1])
        self.itemconfigure(item, font=font)
    for item in self._image:  # 图像大小缩放（采用相对的绝对缩放）
        if self._image[item][0] and self._image[item][0].extension != 'gif':
            self._image[item][1] = self._image[item][0].zoom(
                temp_x*rate_x, temp_y*rate_y, 1.2)
            self.itemconfigure(item, image=self._image[item][1])

def launch(funcid):
    '''根据传入的字符串找到并执行函数'''
    funcid_splited=funcid.split('.')
    match funcid_splited[0]:
        case 'sidebar': #侧边栏按钮
            match funcid_splited[1]:
                case '0':
                    change_sidept_page('file')
                case '1':
                    print('code')
                case '2':
                    print('function')
                case '3':
                    print('class')
                case '4':
                    print('modules')
                case _:
                    msgbox.showerror('错误','launch()没有根据给定的id找到相应的函数\n出错id层级: '+funcid_splited[1])
        case 'sidebarbtm': #侧边栏底部按钮 顺序从下到上
            match funcid_splited[1]:
                case '0':
                    print('more')
                case '1':
                    print('run')
                case _:
                    msgbox.showerror('错误','launch()没有根据给定的id找到相应的函数\n出错id层级: '+funcid_splited[1])
        case _:
            msgbox.showerror('错误','launch()没有根据给定的id找到相应的函数\n出错id层级: '+funcid_splited[0])

def change_sidept_page(pagename):
    global fileframe
    sidept_pages={'file':fileframe}
    global global_sidept_currpage
    sidept_pages[global_sidept_currpage].pack_forget()
    sidept_pages[pagename].pack(fill=tk.BOTH,expand=True)
    sidept_pages[pagename].pack_propagate(False)


root.deiconify()
root.title('Python Visual Programmer')
root.iconbitmap("./icon.ico")
root.configure(background='#cccccc')
root.minsize(540,320)
root.geometry("1920x1018+0+0")

btmbar=tk.Frame(root,bg='#1e1e1e',height=20)
btmbar.pack(side=tk.BOTTOM,fill=tk.X)

sidebar=tk.Frame(root,bg='#1e1e1e',width=48)
sidebar.pack(side=tk.LEFT,fill=tk.Y)
sidebar.pack_propagate(False)

#print(sidebarimg)
tmp_index=0
for img in sidebarimg:
    tk.Button(sidebar,image=img,bg='#1e1e1e',bd=0,command=lambda index=tmp_index:launch('sidebar.'+str(index))).pack(padx=2,pady=2,side=tk.TOP)
    tmp_index+=1

tmp_index=0
for img in sidebarbtmimg:
    tk.Button(sidebar,image=img,bg='#1e1e1e',bd=0,command=lambda index=tmp_index:launch('sidebarbtm.'+str(index))).pack(padx=2,pady=2,side=tk.BOTTOM)
    tmp_index+=1

sidept=tk.Frame(root,bg='#ffffff',width=200)

global_sidept_currpage='file'

fileframe=tk.Frame(sidept,bg='#ffffff',width=200)
tk.Label(fileframe,text='FILES',bg='#ffffff',anchor='w').pack(fill=tk.X)

open_dir(path)
left_frame.pack(fill=tk.BOTH, expand=True)
code_text.place(x=sidebar['width']+sidept['width'], y=0, width=1920-200-48, height=1018)

fileframe.pack_propagate(False)

sidept.pack(side=tk.LEFT,fill=tk.Y)

status_color='#00aa00'
statuspt=tk.Frame(btmbar,width=sidebar['width'],height=btmbar['height'],bg=status_color)
statustxt=tk.Label(statuspt,bg=status_color,text='状态',fg='#ffffff')
statustxt.pack(fill=tk.BOTH,expand=True)
statuspt.pack(side=tk.LEFT,fill=tk.Y)
statuspt.pack_propagate(False)

root.update()

print('root width   ',root.winfo_width())
print('sidebar width   ',sidebar['width'])
print('sidept width   ',sidept['width'])
print('canvas width   ',root.winfo_width()-sidebar['width']-sidept['width'])

root.update()

canvasresize_t=threading.Thread(target=lambda:resize(root,notframex=sidebar['width']+sidept['width'],notframey=btmbar['height']))
canvasresize_t.start()

sync_t.start()

root.mainloop()
