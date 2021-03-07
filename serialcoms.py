import sys
import serial
from time import sleep


class SerialIO():
    def __init__(self):
        self.setup()

    def setup(self):
        self.arduinoData = serial.Serial('COM3', 9600)
        sleep(2)
        self.arduinoData.write('4'.encode('utf-8')) # Forçando modo 4 (MPU)
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()

    def read(self):
        return self.arduinoData.read_all().decode('utf-8')