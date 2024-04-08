import sys

from PySide6.QtWidgets import QMainWindow,QApplication, QCheckBox

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

        checkbox = QCheckBox()
        checkbox.setCheckState(CheckState.Checked)

        # For tristate: widget.setCheckState(Qt.PartiallyChecked)
        # Or: widget.setTriState(True)
        checkbox.stateChanged.connect(self.show_state)

        self.setCentralWidget(checkbox)

    def show_state(self, state):
        print(state == Qt.CheckState.Checked.value)
        print(state)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()