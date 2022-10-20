from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint

import numpy as np
import math
import openpyxl
from smbus2 import SMBus, i2c_msg

wb = openpyxl.Workbook()
sheet = wb.active
sheet['A1'] = 'Dorsi & Plantar'
sheet['B1'] = 'Inversion & Eversion'
sheet['C1'] = 'STJ1'
def getAngle(s1, s2, s3):
    m1 = math.sqrt((s1[0] - s2[0])**2 + (s1[1] - s2[1])**2 + (s1[2] - s2[2])**2)
    m2 = math.sqrt((s3[0] - s2[0])**2 + (s3[1] - s2[1])**2 + (s3[2] - s2[2])**2)
    return m1 + m2

def getSTJ1(s1, s2):
    return math.sqrt((s1[0] - s2[0])**2 + (s1[1] - s2[1])**2 + (s1[2] - s2[2])**2)
    
def getSTJ2(s1, s2):
    return math.sqrt((s1[0] - s2[0])**2 + (s1[1] - s2[1])**2 + (s1[2] - s2[2])**2)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.channel = 1
        self.bus = SMBus(self.channel)
        self.unit = 6
        self.LEN_DATA42 = 42
        # (100 x 7 x 3)
        self.sensors7_3_100 = [[[0]*3 for _ in range(7)] for _ in range(100)]
        self.DP1 = 0
        self.DP2 = 1
        self.DP3 = 2
        self.IE1 = 3
        self.IE2 = 1
        self.IE3 = 4
        self.STJ1 = 6
        self.STJ2 = 3
        self.STJ3 = 4

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setYRange(-180, 180, padding=0)


        #(7 x 3)
        for j in range(100):
            msg = i2c_msg.read(8, 42)
            self.bus.i2c_rdwr(msg)
            data42 = list(msg)
            data7_6 = [data42[i:i+self.unit] for i in range(0, self.LEN_DATA42, self.unit)]
            for idx, sen in enumerate(data7_6): # 7 loop
                Head = np.int16(sen[1]<<8 | sen[0])/16
                if Head > 180: Head -= 360
                Roll = np.int16(sen[3]<<8 | sen[2])/16
                Pitch = np.int16(sen[5]<<8 | sen[4])/16
                self.sensors7_3_100[j][idx][0],self.sensors7_3_100[j][idx][1],self.sensors7_3_100[j][idx][2] = Head,Roll, Pitch

        self.x = list(range(100))  # 100 time points
        #0th sensor, Head  --> 100 values
        #self.y1 = [self.sensors7_3_100[j][self.SENSOR_ST][0] for j in range(100)] 
        #0th sensor, Roll  --> 100 values
        #self.y2 = [self.sensors7_3_100[j][self.SENSOR_ST][1] for j in range(100)] 
        #0th sensor, Pitch --> 100 values
        #self.y3 = [self.sensors7_3_100[j][self.SENSOR_ST][2] for j in range(100)] 

        self.DP = [ getAngle(self.sensors7_3_100[j][self.DP1], self.sensors7_3_100[j][self.DP2], self.sensors7_3_100[j][self.DP3]) for j in range(100)] 
        
        self.IE = [ getAngle(self.sensors7_3_100[j][self.IE1],self.sensors7_3_100[j][self.IE2],self.sensors7_3_100[j][self.IE3]) for j in range(100)] 
        
        self.STJL1 = [ getAngle(self.sensors7_3_100[j][6], self.sensors7_3_100[j][3], self.sensors7_3_100[j][4]) for j in range(100)] 
        
        self.STJL2 = [ getSTJ2(self.sensors7_3_100[j][6], self.sensors7_3_100[j][5]) for j in range(100)] #0th sensor, Pitch --> 100 values
        
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()
        pen1 = pg.mkPen(color=(255, 0, 0))
        pen2 = pg.mkPen(color=(0, 255, 0))
        pen3 = pg.mkPen(color=(0, 0, 255))
        pen4 = pg.mkPen(color=(0, 255, 255))
        
        #self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen1)
        self.data_line1 =  self.graphWidget.plot(self.x, self.DP, name="Dorsi & Plantar", pen=pen1)
        self.data_line2 =  self.graphWidget.plot(self.x, self.IE, name="Inversion & Eversion", pen=pen2)
        self.data_line3 =  self.graphWidget.plot(self.x, self.STJL1, name="STJ1", pen=pen3)
        self.data_line4 =  self.graphWidget.plot(self.x, self.STJL2, name="STJ2", pen=pen4)
        
        # ... init continued ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        
    #def getAngle(s1, s2, s3):
        #'''
        #s1 = self.sensors7_3_100[j][IDX][0] ~ [2]
        #'''
        #return 0            

    def update_plot_data(self):
        sensors7_3 = [[0]*3 for _ in range(7)]
        msg = i2c_msg.read(8, 42)
        self.bus.i2c_rdwr(msg)
        data42 = list(msg)
        data7_6 = [data42[i:i+self.unit] for i in range(0, self.LEN_DATA42, self.unit)]
        for idx, sen in enumerate(data7_6): # 7 loop
            Head = np.int16(sen[1]<<8 | sen[0])/16
            if Head > 180: Head -= 360
            Roll = np.int16(sen[3]<<8 | sen[2])/16
            Pitch = np.int16(sen[5]<<8 | sen[4])/16
            sensors7_3[idx][0],sensors7_3[idx][1],sensors7_3[idx][2] = Head,Roll, Pitch
       
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        '''
        self.y1 = self.y1[1:]  # Remove the first
        self.y1.append(sensors7_3[self.SENSOR_ST][0])  # Add a new random value.

        self.y2 = self.y2[1:]  # Remove the first
        self.y2.append(sensors7_3[self.SENSOR_ST][1])  # Add a new random value.
       
        self.y3 = self.y3[1:]  # Remove the first
        self.y3.append(sensors7_3[self.SENSOR_ST][2])  # Add a new random value.
        '''
        self.DP = self.DP[1:]  # Remove the first
        self.DP.append(getAngle(sensors7_3[0], sensors7_3[1], sensors7_3[2])) 

        self.IE = self.IE[1:]  # Remove the first
        self.IE.append(getAngle(sensors7_3[3], sensors7_3[1], sensors7_3[4]))
       
        self.STJL1 = self.STJL1[1:]  # Remove the first
        self.STJL1.append(getAngle(sensors7_3[6], sensors7_3[3], sensors7_3[4]))  

        self.STJL2 = self.STJL2[1:]  # Remove the first
        self.STJL2.append(getSTJ2(sensors7_3[6], sensors7_3[5]))  
                
        self.data_line1.setData(self.x, self.DP)  # Update the data.
        self.data_line2.setData(self.x, self.IE)  # Update the data.
        self.data_line3.setData(self.x, self.STJL1)  # Update the data.
        self.data_line4.setData(self.x, self.STJL2)  # Update the data.

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
wb.save('Log.xlsx')
sys.exit(app.exec_())	
