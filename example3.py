from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint

import numpy as np
from smbus2 import SMBus, i2c_msg

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.channel = 1
        self.bus = SMBus(self.channel)
        self.unit = 6
        self.LEN_DATA42 = 42
        self.sensors7_3 = [[0]*3 for _ in range(7)] 

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points
        self.y2 = [randint(-50,50) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        #self.data_line2 =  self.graphWidget.plot(self.x, self.y2, pen=pen)

        # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        msg = i2c_msg.read(8, 42)
        self.bus.i2c_rdwr(msg)
        data42 = list(msg)
        data7_6 = [data42[i:i+self.unit] for i in range(0, self.LEN_DATA42, self.unit)]
        for idx, sen in enumerate(data7_6): # 7 loop
            Head = np.int16(sen[1]<<8 | sen[0])/16 
            Roll = np.int16(sen[3]<<8 | sen[2])/16 
            Pitch = np.int16(sen[5]<<8 | sen[4])/16
            self.sensors7_3[idx][0],self.sensors7_3[idx][1],self.sensors7_3[idx][2] = Head,Roll, Pitch 
        
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.

        self.y2 = self.y2[1:]  # Remove the first
        self.y2.append( randint(-50,50))  # Add a new random value.
        
        self.data_line.setData(self.x, self.y)  # Update the data.
        #self.data_line2.setData(self.x, self.y2)  # Update the data.


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
