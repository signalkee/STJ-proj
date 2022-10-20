# i2ctest.py
# A brief demonstration of the Raspberry Pi I2C interface, using the Sparkfun
# Pi Wedge breakout board and a SparkFun MCP4725 breakout board:
# https://www.sparkfun.com/products/8736

import numpy as np
import time
from smbus2 import SMBus, i2c_msg

# I2C channel 1 is connected to the GPIO pins
channel = 1

#  MCP4725 defaults to address 0x60
#address = 0x08

# Register addresses (with "normal mode" power-down bits)
#reg_write_dac = 0x40


# Initialize I2C (SMBus)
bus = SMBus(channel)

#GPIOB = 0x13

unit = 6
LEN_DATA42 = 42
sensors7_3 = [[0]*3 for _ in range(7)] 

while True:
    msg = i2c_msg.read(8, 42)
    bus.i2c_rdwr(msg)
    data42 = list(msg)
    data7_6 = [data42[i:i+unit] for i in range(0, LEN_DATA42, unit)]
    for idx, sen in enumerate(data7_6): # 7 loop
        Head = np.int16(sen[1]<<8 | sen[0])/16 
        if Head > 180: Head -= 360 
        Roll = np.int16(sen[3]<<8 | sen[2])/16 
        Pitch = np.int16(sen[5]<<8 | sen[4])/16
        sensors7_3[idx][0],sensors7_3[idx][1],sensors7_3[idx][2] = Head,Roll, Pitch 
        print(Head,' ', Roll, ' ', Pitch)
        #print(sen)
    #print(sensors7_3)
    #print('')

    #for val in msg:
    #    print(val,end='')
    #print('')
    #delay(1000)
    time.sleep(1)

#while (True):
    #bus.read_i2c_block_data(address, reg_write_dac)
    #portb = bus.read_byte_data(address, GPIOB)
    #portb = bus.read_block_data(address, GPIOB)
    #print(portb)

    #print(bus)
    #print(bus.read_byte(address))

