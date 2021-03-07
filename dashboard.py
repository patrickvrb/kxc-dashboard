import sys
import random
from serialcoms import SerialIO
from PyQt5 import QtCore, QtWidgets, QtChart
from PyQt5.Qt import Qt 
from PyQt5.QtGui import QPainter

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
    
    def setup(self):
        self.serial = SerialIO()
        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setWindowTitle('KXC Dashboard')

        self.button.clicked.connect(self.magic)
        self.button.resize(self.button.sizeHint())
        
    def magic(self):
        self.text.setText(self.serial.read())
        # self.text.setText(random.choice(self.hello))
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 400)
    widget.show()

    sys.exit(app.exec_())