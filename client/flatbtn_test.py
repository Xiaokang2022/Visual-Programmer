import pyvpmodules.ui as ui
import tkinter as tk
import tkinter.messagebox as msgbox


win=tk.Tk()
win.title('FlatButton Test')


tk.Label(win,text='Flat button is a fake button class inherited from tk.Label. \nIt is aimed to provide a modern look for buttons in tkinter.').pack(fill=tk.X)


btn=ui.FlatButton(win,text='FlatButton',command=lambda:msgbox.showinfo('Message','You clicked the button'))
btn.pack(padx=25,pady=10)

costombtn=ui.FlatButton(win,text='FlatButton',bg='#cccccc',fg='#000000',floatingbg='#000000',floatingfg='#ffffff',
                        command=lambda:msgbox.showinfo('Message','You clicked the button'))
costombtn.pack(padx=25,pady=10)

disabledbtn=ui.FlatButton(win,text='FlatButton',bg='#cccccc',fg='#000000',floatingbg='#000000',floatingfg='#ffffff',
                        command=lambda:msgbox.showinfo('Message','You clicked the button'))
disabledbtn.pack(padx=25,pady=10)
disabledbtn.disable()
print(disabledbtn.disablefg)

anmbtn=ui.AnimatedButton(win,win,text='AnimatedButton',bg='#cccccc',fg='#000000',floatingbg='#000000',floatingfg='#ffffff',
                        command=lambda:msgbox.showinfo('Message','You clicked the button'))
anmbtn.pack(padx=25,pady=10)


win.mainloop()
