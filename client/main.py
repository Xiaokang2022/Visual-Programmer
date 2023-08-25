# Python Visual Designer
# 2023 By 小康2022 & 真_人工智障
# v0.1.0

import tkinter as tk
import tkinter.ttk as ttk
import tkintertools as tkt
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
def resize(parent, #type: Tk | Toplevel
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

def _resize(self, rate_x=None, rate_y=None):  # type: (float | None, float | None) -> None
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
root.geometry('720x480')


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

main_file_viewer=ui.FileTree(fileframe)
main_file_viewer.left_frame.pack(fill=tk.BOTH,expand=True)
main_file_viewer.open_dir()

fileframe.pack_propagate(False)

file_rightclick_menu=ui.Menu(root,{'剪切':lambda:pyvpclipboard.cut(main_file_viewer.tree.item(main_file_viewer.tree.focus())['values'][0],'file'),
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

main_file_viewer.sync_t.start()

root.mainloop()
