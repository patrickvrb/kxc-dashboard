import sys  # We need sys so that we can pass argv to QApplication
from random import randint

import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QBoxLayout, QGridLayout,
                             QHBoxLayout, QMenu, QPushButton, QVBoxLayout,
                             QWidget)
from pyqtgraph import PlotWidget, plot

from engine import SerialIO


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.engine = SerialIO()
        self.engine.ard_dump_mode()  # Realiza dump do arduino em engine.py
        self.layout_init()
        # self.upload_data()

    def layout_init(self):
        self.list_button_init()
        self.upload_data()
        self.setWindowTitle('KXC Dashboard')

        grid = QGridLayout()
        self.setLayout(grid)

        positions = [(i, j) for i in range(2) for j in range(2)]

        grid.addWidget(self.graphWidget, 0, 0)
        grid.addWidget(self.drop_button, 2, 2)

        self.move(300, 150)
        self.setWindowTitle('KXC Dashboard')
        self.show()

    def list_button_init(self):
        self.drop_button = QPushButton('CERVEJAS', self)
        self.drop_button.resize(100, 32)
        self.drop_button.move(200, 200)
        menu = QMenu(self)
        menu.addAction('IPA')
        menu.addSeparator()
        menu.addAction('LAGER')
        menu.addSeparator()
        menu.addAction('STOUT')
        self.drop_button.setMenu(menu)
        # pybutton.clicked.connect(self.clickMethod)

    def upload_data(self):
        self.graphWidget = pg.PlotWidget()
        self.y = self.engine.get_angle_list()
        self.x = list(range(len(self.y)))  # y time points
        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

    def update_plot_data(self, data):

        self.x = self.x[1:]  # Remove the first y element.
        # Add a new value 1 higher than the last.
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]  # Remove the first
        self.y.append(data)  # Add the new value.

        self.data_line.setData(self.x, self.y)  # Update the data.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
