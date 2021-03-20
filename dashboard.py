import sys  # We need sys so that we can pass argv to QApplication
from random import randint

import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from pyqtgraph import PlotWidget, plot

from engine import SerialIO


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        engine = SerialIO()
        engine.ard_dump_mode()  # Realiza dump do arduino em engine.py
        self.upload_data()

    def upload_data(self):
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.y = list()
        f = open('flash_dump.txt', 'r')
        while f.readline():
            # Data points, removendo \n
            self.y.append(int(f.readline().rstrip()))
        f.close()

        self.x = list(range(len(self.y)))  # y time points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 255, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

    def update_plot_data(self, data):

        self.x = self.x[1:]  # Remove the first y element.
        # Add a new value 1 higher than the last.
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]  # Remove the first
        self.y.append(data)  # Add the new value.

        self.data_line.setData(self.x, self.y)  # Update the data.


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
