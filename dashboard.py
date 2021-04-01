import sys  # We need sys so that we can pass argv to QApplication

import pyqtgraph as pg
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout, QMenu,
                             QPushButton, QStyle, QWidget)

from engine import SerialIO


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.engine = SerialIO()
        self.layout_init()
        # self.upload_data()

    def layout_init(self):
        self.list_button_init()
        self.setWindowTitle('KXC Dashboard')
        self.setMinimumSize(500, 200)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.drop_button, 2, 2)

        self.show()

    def list_button_init(self):
        self.drop_button = QPushButton('CERVEJAS', self)
        self.drop_button.resize(100, 32)
        self.drop_button.move(200, 200)
        menu = QMenu(self)
        dir_list = self.engine.get_directories()
        for beer in dir_list:
            action = QAction(beer.name, self)
            action.triggered.connect(
                lambda: self.fetch_data(beer))
            menu.addAction(action)
            menu.addSeparator()
        self.drop_button.setMenu(menu)

    def fetch_data(self, beer):
        print(beer.index)
        self.graphWidget = pg.PlotWidget()
        self.engine.ard_dump_mode(beer)
        self.y = self.engine.get_angle_list(beer.name)
        self.x = list(range(len(self.y)))  # y time points
        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)
        self.grid.addWidget(self.graphWidget, 0, 0)
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
