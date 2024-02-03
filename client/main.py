# Python Visual Programmer
# 2023 By 小康2022 & 真_人工智障
# v0.1.0

import tkinter as tk
import tkinter.ttk as ttk
import tkintertools as tkt
import tttk
import tkinter.messagebox as msgbox
import os
import sys
import time
from PIL import ImageTk,Image
import threading
import math
import pyvpmodules.ui as ui
import pyvpmodules.clipboard as clipboard
import pyclip
import webbrowser
import socket
import json
import warnings


#全局变量
global_ver='.beforever'
global_debug={'net':False}
global_server_addr=('116.198.35.73',10009)
global_about_useslist={'Python':"https://www.python.org/",'xiaokang2022/tkintertools':"https://github.com/xiaokang2022/tkintertools/",
                       'spyoungtech/pyclip':"https://github.com/spyoungtech/pyclip/",'totowang-hhh/tttk':"https://github.com/totowang-hhh/tttk/"}

os.chdir(os.path.split(os.path.realpath(__file__))[0])
print(os.getcwd())
#os.chdir(sys.argv[0])

pyvpclipboard=clipboard.Clipboard()

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


# 类与函数
def resize(parent, #type: tk.Tk | tk.Toplevel
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

def _resize(self, rate_x=None, rate_y=None):
    """
    ### 缩放画布及其内部的所有元素
    `rate_x`: 横向缩放比率，默认值表示自动更新缩放（根据窗口缩放程度） \ 
    `rate_y`: 纵向缩放比率，默认值同上
    """
    if not rate_x:
        rate_x = self.master.width[1]/self.master.width[0]/self.rx
    if not rate_y:
        rate_y = self.master.height[1]/self.master.height[0]/self.ry
    rate_x_pos, rate_y_pos = rate_x, rate_y  # 避免受 keep 影响
    if self.keep is True:  # 维持比例
        rx = rate_x*self.master.width[1]/self.master.width[0]/self.rx
        ry = rate_y*self.master.height[1]/self.master.height[0]/self.ry
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

def get_fr_server(send_data):
    global global_server_addr
    skt=socket.socket()
    skt.connect(global_server_addr)
    skt.send(json.dumps(send_data).encode('utf-8'))
    res=json.loads(skt.recv(1024).decode('utf-8'))
    skt.close()
    return res

def change_sidept_page(pagename):
    global fileframe
    sidept_pages={'file':fileframe}
    global global_sidept_currpage
    sidept_pages[global_sidept_currpage].pack_forget()
    sidept_pages[pagename].pack(fill=tk.BOTH,expand=True)
    sidept_pages[pagename].pack_propagate(False)

def about():
    global global_ver,about_updtxt,global_server_addr,global_about_useslist
    aboutwin=tk.Toplevel()
    aboutwin.title('关于PyVP')
    aboutwin.transient(root)
    aboutwin.configure(background='#ffffff')
    #ui.blur_window_background(aboutwin)
    about_pt=tk.Frame(aboutwin,bg='#ffffff')
    icon128_pil=icon_pil.resize((128,128))
    icon128_tk=ImageTk.PhotoImage(image=icon128_pil)
    tk.Label(about_pt,image=icon128_tk,bg='#ffffff').pack(side=tk.LEFT)
    abouttxtpt=tk.Frame(about_pt,bg='#ffffff')
    tk.Label(abouttxtpt,text='Python Visual Programmer',bg='#ffffff',font=('微软雅黑',20),anchor='w').pack()
    aboutrowb=tk.Frame(abouttxtpt,bg='#ffffff')
    tk.Label(aboutrowb,text='2023 By 小康2022 & 真_人工智障',bg='#ffffff',anchor='w').pack(side=tk.LEFT)
    tk.Label(aboutrowb,text='v'+global_ver,bg='#ffffff',fg='#909090',anchor='e').pack(side=tk.RIGHT)
    aboutrowb.pack(fill=tk.X)
    ttk.Separator(abouttxtpt).pack(fill=tk.X,pady=10)
    aboutrowc=tk.Frame(abouttxtpt,bg='#ffffff')
    about_updtxt=tk.Label(aboutrowc,text='请等待版本检查就绪',bg='#ffffff',anchor='w')
    about_updtxt.pack(side=tk.LEFT)
    ui.AnimatedButton(aboutrowc,aboutwin,text='项目GitHub',bg='#cccccc',fg='#000000',floatingbg='#000000',floatingfg='#ffffff',
              command=lambda:webbrowser.open("https://github.com/xiaokang2022/visual-programmer")).pack(side=tk.RIGHT)
    aboutrowc.pack(fill=tk.X)
    uses_pt=tk.Frame(aboutwin,bg='#dddddd')
    tk.Label(uses_pt,text='本项目使用',bg='#303030',fg='#ffffff').pack(fill=tk.X)
    ulist_pt=tk.Frame(uses_pt,bg='#dddddd')
    ulist_cola=tk.Frame(ulist_pt,bg='#dddddd')
    ulist_colb=tk.Frame(ulist_pt,bg='#dddddd')
    curr_col=0
    for proj in global_about_useslist.keys():
        if curr_col==0:
            txt=tk.Label(ulist_cola,text=proj,bg='#dddddd',anchor='w')
            curr_col=1
        elif curr_col==1:
            txt=tk.Label(ulist_colb,text=proj,bg='#dddddd',anchor='w')
            curr_col=0
        else:
            warnings.warn('Uses list packing failed')
        txt.bind("<Button-1>",lambda event,url=global_about_useslist[proj]:webbrowser.open(url))
        txt.pack(fill=tk.X)
    ulist_cola.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
    ulist_colb.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)
    ulist_pt.pack(fill=tk.BOTH,expand=True)
    about_pt.pack(fill=tk.X)
    uses_pt.pack(fill=tk.X,padx=10,pady=10)
    abouttxtpt.pack(fill=tk.BOTH,side=tk.RIGHT,padx=15)
    aboutwin.update()
    aboutwin.resizable(False,False)
    try:
        res=get_fr_server({"func":"ver.get_ifnewver","clientver":global_ver})
        #print(res)
        about_updtxt['text']=res['msg']
    except:
        about_updtxt['text']='暂时无法检查更新'
    aboutwin.mainloop()

def submit_server_addr(ip_enter,port_enter,askwin=None):
    global global_server_addr
    isvalid=True
    #for pt in ip_enter.get().split('.'):
    #    if not pt.isdigit():
    #        isvalid=False
    if not port_enter.get().isdigit():
        isvalid=False
    if isvalid:
        global_server_addr=(ip_enter.get(),int(port_enter.get()))
    print(get_fr_server({"func":"connection.check","ver":global_ver}))
    if not get_fr_server({"func":"connection.check","ver":global_ver})['response']:
        isvalid=False
    if isvalid:
        if askwin!=None:
            askwin.destroy()
    else:
        msgbox.showerror('输入信息无效','指定的服务器配置信息无效\n请编辑确认后再次提交')

def ask_server_addr(root_win=None):
    askaddr_win=tk.Toplevel()
    if root_win!=None:
        askaddr_win.transient(root_win)
    askaddr_win.title('指定服务器')
    ip_enter=tttk.TipEnter(askaddr_win,text='地址')
    #ip_enter.tip['anchor']='e'
    #ip_enter.tip['width']=6
    ip_enter.pack(fill=tk.X)
    port_enter=tttk.TipEnter(askaddr_win,text='端口')
    #port_enter.tip['anchor']='e'
    #port_enter.tip['width']=6
    port_enter.pack(fill=tk.X)
    ttk.Button(askaddr_win,text='提交',command=lambda:submit_server_addr(ip_enter,port_enter,askaddr_win)).pack(fill=tk.X)
    askaddr_win.update()
    askaddr_win.geometry('300x'+str(askaddr_win.winfo_height()))
    askaddr_win.resizable(0,0)
    askaddr_win.mainloop()

def change_file(selection:str):
    # 在边栏文件列表中切换文件时执行
    global view_btns
    file=selection['values'][0]
    print("已选择文件："+str(file))
    # 根据文件后缀决定是否允许视图切换
    if file.split('.')[len(file.split('.'))-1].lower()=='py':
        #print('Still not availale')
        for btn in view_btns:
            btn.enable()
    else:
        for btn in view_btns:
            btn.disable()
            #print(btn.disablefg,btn.fg)


root.deiconify()
root.title('Python Visual Programmer')
root.iconbitmap("./icon.ico")
root.configure(background='#cccccc')
root.minsize(540,320)
root.geometry('720x480')

#py_win_style.apply_style(root,'aero')

btmbar=tk.Frame(root,bg='#1e1e1e',height=24)
btmbar.pack(side=tk.BOTTOM,fill=tk.X)

sidebar=tk.Frame(root,bg='#1e1e1e',width=48)
sidebar.pack(side=tk.LEFT,fill=tk.Y)
sidebar.pack_propagate(False)

#print(sidebarimg)
tmp_index=0
for img in sidebarimg:
    ui.FlatButton(sidebar,image=img,bg='#1e1e1e',floatingbg='nochange',command=lambda index=tmp_index:launch('sidebar.'+str(index))).pack(padx=2,pady=2,side=tk.TOP)
    tmp_index+=1

tmp_index=0
for img in sidebarbtmimg:
    ui.FlatButton(sidebar,image=img,bg='#1e1e1e',floatingbg='nochange',command=lambda index=tmp_index:launch('sidebarbtm.'+str(index))).pack(padx=2,pady=2,side=tk.BOTTOM)
    tmp_index+=1

sidept=tk.Frame(root,bg='#ffffff',width=200)

global_sidept_currpage='file'

fileframe=tk.Frame(sidept,bg='#ffffff',width=200)
tk.Label(fileframe,text='FILES',bg='#ffffff',anchor='w').pack(fill=tk.X)

main_file_viewer=ui.FileTree(fileframe,selcommand=change_file)
main_file_viewer.left_frame.pack(fill=tk.BOTH,expand=True)
main_file_viewer.open_dir()

fileframe.pack_propagate(False)

file_rightclick_menu=tttk.Menu(root,{'剪切':lambda:pyvpclipboard.cut(main_file_viewer.tree.item(main_file_viewer.tree.focus())['values'][0],'file'),
                                     '复制':lambda:pyvpclipboard.copy(main_file_viewer.tree.item(main_file_viewer.tree.focus())['values'][0],'file'),
                                     '粘贴':lambda:pyvpclipboard.paste_at_file(main_file_viewer.get_focus_dir()),
                                     '永久删除':lambda:print('del'),'重命名':lambda:print('rename')})
main_file_viewer.tree.bind('<Button-3>',lambda event:file_rightclick_menu.show() if len(main_file_viewer.tree.focus())!=0 else None)

sidept.pack(side=tk.LEFT,fill=tk.Y)

status_color='#00aa00'
statuspt=tk.Frame(btmbar,width=sidebar['width'],height=btmbar['height'],bg=status_color)
statustxt=tk.Label(statuspt,bg=status_color,text='状态',fg='#ffffff')
statustxt.pack(fill=tk.BOTH,expand=True)
statuspt.pack(side=tk.LEFT,fill=tk.Y)
statuspt.pack_propagate(False)

about_txt=tk.Button(btmbar,text='Python Visual Programmer v'+global_ver,bg='#1e1e1e',fg='#ffffff',bd=0,font=('微软雅黑',7),command=about).pack(side=tk.RIGHT,fill=tk.Y)

view_switch=tk.Frame(btmbar)
view_btns=[ui.FlatButton(view_switch,'顺序视图',bg='#1e1e1e',fg='#ffffff',floatingbg='lighter',floatingfg='nochange',disablefg='darker'),
           ui.FlatButton(view_switch,'蓝图视图',bg='#1e1e1e',fg='#ffffff',floatingbg='lighter',floatingfg='nochange',disablefg='darker')]
for btn in view_btns:
    btn.pack(side=tk.LEFT,fill=tk.Y)
view_switch.pack(side=tk.RIGHT,fill=tk.Y)

root.update()

win=tkt.Canvas(root,width=root.winfo_width()-sidebar['width']-sidept['width'],
                    height=root.winfo_height()-btmbar['height'],
                    x=sidebar['width']+sidept['width'],y=0,expand=False)

print('root width   ',root.winfo_width())
print('sidebar width   ',sidebar['width'])
print('sidept width   ',sidept['width'])
print('canvas width   ',root.winfo_width()-sidebar['width']-sidept['width'])

root.update()

win.place(x=sidebar['width']+sidept['width'],y=0)

canvasresize_t=threading.Thread(target=lambda:resize(root,notframex=sidebar['width']+sidept['width'],notframey=btmbar['height']))
canvasresize_t.start()

tkt.Label(win, 50, 50, 250, 100, text='工作区（主区域）\n此处待完善')

# 手动指定服务器
if global_server_addr=='ask':
    ask_server_addr(root_win=root)

main_file_viewer.sync_t.start()

root.mainloop()
