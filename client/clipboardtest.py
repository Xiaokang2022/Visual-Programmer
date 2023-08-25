# coding=utf-8

import pyvpmodules.clipboard as clipboard
import tkinter as tk
import tkinter.ttk as ttk
import tttk
import pyclip

clipboard=clipboard.Clipboard()

win=tk.Tk()
win.title('PyVP Modules > ClipBoard TEST')

copy_enterbox=tttk.TipEnter(win,text='复制到剪贴板',command=lambda:print('loading'),btntxt='→复制')
copy_enterbox.command=lambda:clipboard.copy(copy_enterbox.get(),'text')
copy_enterbox.refresh()
copy_enterbox.pack(fill=tk.X)

cut_enterbox=tttk.TipEnter(win,text='剪切到剪贴板',command=lambda:print('loading'),btntxt='→剪切')
cut_enterbox.command=lambda:clipboard.cut(cut_enterbox.get(),'text')
cut_enterbox.refresh()
cut_enterbox.pack(fill=tk.X)

paste_enterbox=tttk.TipEnter(win,text='粘贴到输入框',command=lambda:print('loading'),btntxt='←粘贴')
paste_enterbox.command=lambda:clipboard.paste(paste_enterbox.enter,tkinsert=True)
paste_enterbox.refresh()
paste_enterbox.pack(fill=tk.X)

ttk.Button(win,text='清空剪贴板',command=pyclip.clear).pack(fill=tk.X)

win.update()
win.resizable(True,False)

win.mainloop()
