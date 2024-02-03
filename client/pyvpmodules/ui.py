import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filebox
from tkinter import *
import os
import sys
#import pyautogui
import time
import threading

currcwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])

class FileTree(): #这个太屎山了，不想写注释了
    # path = r"E:\\python开发工具\\project\\tkinter"
    path = os.path.abspath(".")
    file_types = [".png", ".jpg", ".jpeg", ".ico", ".gif"]
    scroll_visiblity = True
    
    font = 11
    font_type = "Courier New"
    
    def __init__(self,parent,selcommand=lambda item:print('已选择项目 '+str(item))):
        currcwd=os.getcwd()
        os.chdir(os.path.split(os.path.realpath(__file__))[0])

        # 非界面相关
        self.sel_file="" #当前文件

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
        self.tree.bind("<<TreeviewSelect>>", lambda event:self.on_sel_file())

        os.chdir(currcwd)

        self.sync_t=threading.Thread(target=self.auto_refresh)
    def on_sel_file(self):
        self.sel_file=str(self.tree.item(self.tree.focus()))
        self.selcmd(self.tree.item(self.tree.focus()))
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
    def setcolor(self,btn,newbg,newfg): #设置按钮颜色
        btn['bg']=newbg
        btn['fg']=newfg
    def getpos(self): #获取菜单应该处在的位置
        if self.pos=='cur':
            posx=self.parent.winfo_x()+self.parent.winfo_pointerx()
            posy=self.parent.winfo_y()+self.parent.winfo_pointery()
            return (self.parent.winfo_pointerx(),self.parent.winfo_pointery())
        else:
            return self.pos
    def show(self): #显示菜单
        self.deiconify()
        newx,newy=self.getpos()
        self.geometry(str(self.width)+'x'+str(self.winfo_height())+'+'+str(newx+10)+'+'+str(newy+10))
    def _hide(self): #直接隐藏菜单（无消失动画）
        self.withdraw()
    def hide(self): #消失动画+隐藏菜单
        for i in range(0,5):
            self.wm_attributes('-alpha',1-0.2*i)
            self.update()
            time.sleep(0.02)
        self._hide()
        self.wm_attributes('-alpha',1)
    def do(self,func): #执行选定项并隐藏菜单
        self.hide()
        func()

class FlatButton(tk.Label):
    def __init__(self,parent,text=None,image=None,bg='#0078dc',fg='#ffffff',floatingbg='darker',floatingfg='nochange',disablefg='lighter',command=None):
        if image==None:
            tk.Label.__init__(self,parent,text=text,bg=bg,fg=fg)
        else:
            tk.Label.__init__(self,parent,image=image,bg=bg,fg=fg)
        self.parent=parent
        self.text=text
        self.image=image
        self.bg=bg
        self.fg=fg
        if floatingbg.lower()=='darker':
            self.floatingbg=self.calc_color(self.bg,'darker',level=1)
        elif floatingbg.lower()=='nochange':
            self.floatingbg=self.bg
        elif floatingbg.lower()=='lighter':
            self.floatingbg=self.calc_color(self.bg,'lighter',level=1)
        else:
            self.floatingbg=floatingbg
        if floatingfg.lower()=='nochange':
            self.floatingfg=self.fg
        else:
            self.floatingfg=floatingfg
        if disablefg.lower()=='darker':
            self.disablefg=self.calc_color(self.fg,'darker',level=4)
        elif disablefg.lower()=='lighter':
            self.disablefg=self.calc_color(self.fg,'lighter',level=4)
        else:
            self.disablefg=disablefg
        self.command=command
        self.bind('<Enter>',self.mouse_enter)
        self.bind('<Leave>',self.mouse_leave)
        self.bind('<Button-1>',self.mouse_click)
    def calc_color(self,color:str,change_type:str='darker',level:int=1): #将传入的颜色变深/变浅，用于处理颜色参数中传入的'lighter'/'darker'
        if level==0: #level参数为0代表不处理
            return color
        if color[0]!='#':
            warnings.warn('Invalid or unacceptable color: '+str(hexstr)+'. Color for FlatButton.calc_color() must be a hex color. Using original color!')
            return color
        hexstr=color.replace('#','')
        #print(hexstr[0:2])
        rhex=int(hexstr[0:2],16)
        ghex=int(hexstr[2:4],16)
        bhex=int(hexstr[4:6],16)
        #print(rhex,ghex,bhex)
        for i in range(level):
            match change_type:
                case 'darker':
                    rhex-=32
                    ghex-=32
                    bhex-=32
                case 'lighter':
                    rhex+=32
                    ghex+=32
                    bhex+=32
        if rhex<0:
            rhex=0
        elif rhex>255:
            rhex=255
        if ghex<0:
            ghex=0
        elif ghex>255:
            ghex=255
        if bhex<0:
            bhex=0
        elif bhex>255:
            bhex=255
        #print(rhex,ghex,bhex)
        rstr=str(hex(rhex)).replace('0x','')
        gstr=str(hex(ghex)).replace('0x','')
        bstr=str(hex(bhex)).replace('0x','')
        if len(rstr)<2:
            rstr='0'+rstr
        if len(gstr)<2:
            gstr='0'+gstr
        if len(bstr)<2:
            bstr='0'+bstr
        newcolor='#'+rstr+gstr+bstr
        return newcolor
    def mouse_enter(self,event=''): #鼠标进入时改变颜色
        self['bg']=self.floatingbg
        self['fg']=self.floatingfg
    def mouse_leave(self,event=''): #鼠标离开时恢复颜色
        self['bg']=self.bg
        self['fg']=self.fg
    def mouse_click(self,event=''): #鼠标点击时执行指定的函数，本函数用于防止“None object is not callable”
        if self.command!=None:
            self.command()
    def disable(self): #禁用按钮，取消绑定所有事件并改变颜色
        self.unbind('<Enter>')
        self.unbind('<Leave>')
        self.unbind('<Button-1>')
        self['fg']=self.disablefg
    def enable(self): #启用按钮，重新绑定所有事件并恢复颜色
        self.bind('<Enter>',self.mouse_enter)
        self.bind('<Leave>',self.mouse_leave)
        self.bind('<Button-1>',self.mouse_click)
        self['fg']=self.fg
    def reprop(self): #如果在创建按钮后更改其属性，则本函数用于更新按钮
        #self.__init__()
        self['bg']=self.bg
        self['fg']=self.fg

class AnimatedButton(FlatButton): #请勿大规模使用AnimatedButton()，防止卡顿或bug泛滥
    def __init__(self,parent,win,text=None,image=None,bg='#0078dc',fg='#ffffff',floatingbg='darker',floatingfg='nochange',disablefg='lighter',command=None):
        FlatButton.__init__(self,parent,text=text,image=image,bg=bg,fg=fg,floatingbg=floatingbg,floatingfg=floatingfg,disablefg=disablefg,command=command)
        self.win=win
        self.mousefloating=False
        self.bind('<Enter>',self.animation_enter)
        self.bind('<Leave>',self.animation_leave)
    def rgb2hex(self,rgbcolor, tohex=True,tohexstr=True): #rgb颜色转hex
        '''RGB转HEX

        :param rgbcolor: RGB颜色元组，Tuple[int, int, int]
        :param tohex: 是否转十六进制字符串，默认不转
        :return: int or str

        >>> rgb2hex((255, 255, 255))
        16777215
        >>> rgb2hex((255, 255, 255), tohex=True)
        '0xffffff'
        '''
        r, g, b = rgbcolor
        if r>255:
            r=255
        elif r<0:
            r=0
        if g>255:
            g=255
        elif r<0:
            g=0
        if b>255:
            b=255
        elif b<0:
            b=0
        result = (r << 16) + (g << 8) + b
        if tohexstr:
            result=str(hex(result)).replace('0x','#')
            if result[0]=='-':
                result='#000000'
            if len(result)<7:
                for i in range(7-len(result)):
                    result+='0'
            return result
        return hex(result) if tohex else result
    def hex2rgb(self,hexcolor): #hex颜色转rgb
        '''HEX转RGB

        :param hexcolor: int or str
        :return: Tuple[int, int, int]

        >>> hex2rgb(16777215)
        (255, 255, 255)
        >>> hex2rgb('0xffffff')
        (255, 255, 255)
        '''
        hexcolor = int(hexcolor, base=16) if isinstance(hexcolor, str) else hexcolor
        rgb = ((hexcolor >> 16) & 0xff, (hexcolor >> 8) & 0xff, hexcolor & 0xff)
        return rgb
    def animation_enter(self,event=''): #鼠标进入动画
        self.mousefloating=True
        bg_rgb=self.hex2rgb(self.bg.replace('#','0x'))
        fg_rgb=self.hex2rgb(self.fg.replace('#','0x'))
        floatingbg_rgb=self.hex2rgb(self.floatingbg.replace('#','0x'))
        floatingfg_rgb=self.hex2rgb(self.floatingfg.replace('#','0x'))
        bg_r_steplength=(floatingbg_rgb[0]-bg_rgb[0])//5
        bg_g_steplength=(floatingbg_rgb[1]-bg_rgb[1])//5
        bg_b_steplength=(floatingbg_rgb[2]-bg_rgb[2])//5
        fg_r_steplength=(floatingfg_rgb[0]-fg_rgb[0])//5
        fg_g_steplength=(floatingfg_rgb[1]-fg_rgb[1])//5
        fg_b_steplength=(floatingfg_rgb[2]-fg_rgb[2])//5
        nowfg=list(fg_rgb)
        nowbg=list(bg_rgb)
        for i in range(5):
            if not self.mousefloating:
                return
            nowfg[0]+=fg_r_steplength
            nowfg[1]+=fg_g_steplength
            nowfg[2]+=fg_b_steplength
            nowbg[0]+=bg_r_steplength
            nowbg[1]+=bg_g_steplength
            nowbg[2]+=bg_b_steplength
            self['fg']=self.rgb2hex(nowfg).replace('0x','#')
            self['bg']=self.rgb2hex(nowbg).replace('0x','#')
            self.win.update()
            time.sleep(0.05)
        self.mouse_enter()
    def animation_leave(self,event=''): #鼠标退出动画
        self.mousefloating=False
        bg_rgb=self.hex2rgb(self.bg.replace('#','0x'))
        fg_rgb=self.hex2rgb(self.fg.replace('#','0x'))
        floatingbg_rgb=self.hex2rgb(self.floatingbg.replace('#','0x'))
        floatingfg_rgb=self.hex2rgb(self.floatingfg.replace('#','0x'))
        bg_r_steplength=(floatingbg_rgb[0]-bg_rgb[0])//5
        bg_g_steplength=(floatingbg_rgb[1]-bg_rgb[1])//5
        bg_b_steplength=(floatingbg_rgb[2]-bg_rgb[2])//5
        fg_r_steplength=(floatingfg_rgb[0]-fg_rgb[0])//5
        fg_g_steplength=(floatingfg_rgb[1]-fg_rgb[1])//5
        fg_b_steplength=(floatingfg_rgb[2]-fg_rgb[2])//5
        nowfg=list(floatingfg_rgb)
        nowbg=list(floatingbg_rgb)
        for i in range(5):
            nowfg[0]-=fg_r_steplength
            nowfg[1]-=fg_g_steplength
            nowfg[2]-=fg_b_steplength
            nowbg[0]-=bg_r_steplength
            nowbg[1]-=bg_g_steplength
            nowbg[2]-=bg_b_steplength
            self['fg']=self.rgb2hex(nowfg).replace('0x','#')
            self['bg']=self.rgb2hex(nowbg).replace('0x','#')
            self.win.update()
            time.sleep(0.05)
        self.mouse_leave()
    #def disable(self): #覆盖并移除禁用函数
    #    warnings.warn('AnimatedButton.disable() has been REMOVED.')
    #def enable(self): #覆盖并移除启用函数
    #    warnings.warn('AnimatedButton.enable() has been REMOVED.')
    def enable(self): #覆盖原启用函数
        self.bind('<Enter>',self.animation_enter)
        self.bind('<Leave>',self.animation_leave)
        self.bind('<Button-1>',self.mouse_click)
        self['fg']=self.fg

os.chdir(currcwd)
