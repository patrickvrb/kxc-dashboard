import sys

import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout, QMenu,
                             QPushButton, QWidget)

from engine import SerialIO


class Dashboard(QWidget):

    def __init__(self, *args, **kwargs):
        super(Dashboard, self).__init__(*args, **kwargs)
        self.engine = SerialIO()
        self.layout_init()

    def layout_init(self):
        self.list_button_init()
        self.setWindowTitle('KXC Dashboard')
        self.setWindowIcon(QtGui.QIcon('assets/beer.ico'))
        self.setMinimumSize(750, 450)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.drop_button, 1, 1,
                            Qt.AlignmentFlag.AlignCenter)
        self.show()

    def list_button_init(self):
        self.drop_button = QPushButton('CERVEJAS', self)
        # self.drop_button.resize(100, 32)
        # self.drop_button.move(200, 200)
        menu = QMenu(self)
        dir_list = self.engine.get_directories()
        for dir in dir_list:
            action = QAction(dir.name, self)
            action.triggered.connect(
                lambda _, beer=dir: self.fetch_data(beer))
            menu.addAction(action)
            menu.addSeparator()
        self.drop_button.setMenu(menu)
        self.drop_button.setStyleSheet(self.get_button_stylesheet())
        return

    def fetch_data(self, beer):
        self.engine.ard_dump_mode(beer)
        self.tension_list, self.temp_list, self.angle_list, self.coord_list = self.engine.get_measures_lists(
            beer)

        self.build_graphs()

    def build_graphs(self):
        angles_widget = pg.PlotWidget()
        angles_widget.setTitle('Variação Angular')
        y = self.angle_list
        x = list(range(len(y)))  # y time points
        angles_widget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width=2)
        angles_widget.setLabel('left', 'Ângulo (DEG)')
        angles_widget.setLabel('bottom', 'Medições')
        angles_widget.showGrid(x=True, y=True)
        angles_widget.plot(x, y, pen=pen)

        tension_widget = pg.PlotWidget()
        tension_widget.setTitle('Tensão da bateria')
        y = self.tension_list
        x = list(range(len(y)))  # y time points
        tension_widget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 255), width=2)
        tension_widget.setLabel('left', 'Tensão (V)')
        tension_widget.setLabel('bottom', 'Medições')
        tension_widget.showGrid(x=True, y=True)
        tension_widget.plot(x, y, pen=pen)

        temp_widget = pg.PlotWidget()
        temp_widget.setTitle('Temperatura')
        y = self.temp_list
        x = list(range(len(y)))  # y time points
        temp_widget.setBackground('w')
        pen = pg.mkPen(color=(50, 0, 150), width=2)
        temp_widget.setLabel('left', 'Temperatura (°C)')
        temp_widget.setLabel('bottom', 'Medições')
        temp_widget.showGrid(x=True, y=True)
        temp_widget.plot(x, y, pen=pen)

        coord_widget = pg.PlotWidget()
        coord_widget.setTitle('Coordenadas')
        x_list = list()
        y_list = list()
        z_list = list()
        y = self.coord_list
        for coord in y:
            x_list.append(coord[0])
            y_list.append(coord[1])
            z_list.append(coord[2])

        x = list(range(len(y)))  # y time points
        coord_widget.setBackground('w')
        coord_widget.setLabel('left', 'Valores')
        coord_widget.setLabel('bottom', 'Medições')
        coord_widget.showGrid(x=True, y=True)
        coord_widget.addLegend()
        coord_widget.plot(x, x_list, name="Eixo X", pen=pg.mkPen(
            color=(255, 0, 0), width=2))
        coord_widget.plot(x, y_list, name="Eixo Y", pen=pg.mkPen(
            color=(0, 255, 0), width=2))
        coord_widget.plot(x, z_list, name="Eixo Z", pen=pg.mkPen(
            color=(0, 0, 255), width=2))
        for idx, _ in enumerate(y):
            if idx % 24 == 0:
                angles_widget.addItem(pg.InfiniteLine(
                    pos=idx), ignoreBounds=True)
                temp_widget.addItem(pg.InfiniteLine(
                    pos=idx), ignoreBounds=True)
                tension_widget.addItem(pg.InfiniteLine(
                    pos=idx), ignoreBounds=True)
                coord_widget.addItem(pg.InfiniteLine(
                    pos=idx), ignoreBounds=True)

        self.grid.addWidget(angles_widget, 0, 0)
        self.grid.addWidget(tension_widget, 0, 1)
        self.grid.addWidget(temp_widget, 1, 0)
        self.grid.addWidget(coord_widget, 1, 1)
        self.grid.addWidget(self.drop_button, 2, 0, 1, 2,
                            Qt.AlignmentFlag.AlignCenter)

        return

    def update_plot_data(self, data):

        self.x = self.x[1:]  # Remove the first y element.
        # Add a new value 1 higher than the last.
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]  # Remove the first
        self.y.append(data)  # Add the new value.

        self.data_line.setData(self.x, self.y)  # Update the data.

    def get_button_stylesheet(self):
        return "background-color: white;border-style: outset;border-width: 2px;border-radius: 10px;border-color: orange; font: 14px; min-width: 10.5em;padding: 6px;"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec_())
