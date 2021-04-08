import sys

import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout, QMenu,
                             QPushButton, QWidget)

from engine import SerialIO


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.engine = SerialIO()
        self.layout_init()

    def layout_init(self):
        self.list_button_init()
        self.setWindowTitle('KXC Dashboard')
        self.setWindowIcon(QtGui.QIcon('assets/beer.png'))
        self.setMinimumSize(750, 450)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.drop_button, 1, 1)
        self.show()

    def list_button_init(self):
        self.drop_button = QPushButton('CERVEJAS', self)
        self.drop_button.resize(100, 32)
        self.drop_button.move(200, 200)
        menu = QMenu(self)
        dir_list = self.engine.get_directories()
        for dir in dir_list:
            action = QAction(dir.name, self)
            action.triggered.connect(
                lambda checked, beer=dir: self.fetch_data(beer))
            menu.addAction(action)
            menu.addSeparator()
        self.drop_button.setMenu(menu)
        return

    def fetch_data(self, beer):
        self.engine.ard_dump_mode(beer)
        self.tension_list, self.temp_list, self.angle_list = self.engine.get_measures_lists(
            beer)

        self.build_graphs()

    def build_graphs(self):
        graphWidget = pg.PlotWidget()
        graphWidget.setTitle('Variação Angular')
        y = self.angle_list
        x = list(range(len(y)))  # y time points
        graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        graphWidget.plot(x, y, pen=pen)
        self.grid.addWidget(graphWidget, 0, 0)

        graphWidget = pg.PlotWidget()
        graphWidget.setTitle('Tensão da bateria')
        y = self.tension_list
        x = list(range(len(y)))  # y time points
        graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 255))
        graphWidget.plot(x, y, pen=pen)
        self.grid.addWidget(graphWidget, 0, 1)

        graphWidget = pg.PlotWidget()
        graphWidget.setTitle('Temperatura')
        y = self.temp_list
        x = list(range(len(y)))  # y time points
        graphWidget.setBackground('w')
        pen = pg.mkPen(color=(50, 0, 150))
        graphWidget.plot(x, y, pen=pen)
        self.grid.addWidget(graphWidget, 1, 0)

        return

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
