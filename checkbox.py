import sys
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a checkbox
        checkbox = QCheckBox('Checkbox', self)
        
        # Connect the stateChanged signal to a custom slot (optional)
        checkbox.stateChanged.connect(self.checkboxStateChanged)

        layout.addWidget(checkbox)

        self.setLayout(layout)
        self.setWindowTitle('Checkbox Example')
        self.show()

    def checkboxStateChanged(self, state):
        print(state)
        if state == 2:  # Checked state
            print('Checkbox is checked')
        else:
            print('Checkbox is unchecked')

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
