import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Image Box Example")
        self.setGeometry(100, 100, 400, 300)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)
        
        self.load_image("C:\Jayant\OneDrive\Desktop\Chankya 1.png")  # Change to your image file path
    
    def load_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Image not found")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
