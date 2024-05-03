from dbhelper import *
from errorLogger import *
from tkinter import * 
import sys
#https://www.pythonguis.com/tutorials/pyside6-layouts/
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication

from cameramain import MainWindow
# from tkinter import ttk
# from tkinter import messagebox
class BoroScope:
    def __init__(self,root):
        print('In Constructor of main method')
        self.root = root
        self.root.title('Welcome to Boroscope')
        # print(self.root.winfo_width)
        # print(self.root.winfo_height)
        self.root.geometry('1280x720')
        self.root.iconbitmap('magnetivity_vLw_icon.ico')

        lblTitle=Label(self.root,text='Boroscope',bg='powder blue', fg='green',bd=20, relief=RIDGE,font=('Courier New',20,'bold'),padx=2,pady=6)
        lblTitle.pack(side=TOP,fill=X)

        frame = Frame(self.root,bd=12,relief=RIDGE,padx=20,bg='powder blue')
        frame.place(x=0,y=90,height=400,width=1272)

        # #================== Left Frame===============================

        DataFrameLeft = LabelFrame(frame,text='Processed Information',bg='powder blue', fg='green',bd=12,font=('Courier New',12,'bold'))
        DataFrameLeft.place(x=0,y=5,width=525,height=350)

        # lblMember=Label(DataFrameLeft,bg='powder blue',text="Member Type",font=('Courier New',12,'bold'),textvariable=self.member_var,padx=2,pady=6)
        # lblMember.grid(row=0,column=0,sticky=W)

        # comMember=ttk.Combobox(DataFrameLeft,font=('Courier New',12,'bold'),width=27,state='readonly')
        # comMember["values"]=("Admin Staff","Student","Lecturer")
        # comMember.grid(row=0,column=1)

def main():
    
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    a.exit()
 
    try:
        return a.exec_()
    except AttributeError:
        return a.exec_()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   
    sys.exit(main())
    
    # print('in Main method')
    # logger = LogError.LogError()
    # logger.info(msg='Application Started')

    # root=Tk()
    # br = BoroScope(root)

    # root.mainloop()

    # result = DBHelper.ExecuteQuery('usp_GetRoleList')
    # print(result)

    # if result != None:
    #     for item in result:
    #         number = item['RoleId']
    #         role = item['RoleName']
    #         #print('Number=', number, ',Role=', role)
    #         logger.info('Number='+str(number)+ ',Role='+ role)