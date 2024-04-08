from PyQt6.QtWidgets import QApplication, QMainWindow
import sys
class Employee():
   def __init__(self):
        print('In CTOR')
        
        def Hello():
            print('Hello')
 
a = Employee()
a.__init__.Hello()