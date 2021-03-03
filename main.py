import serial
from time import sleep

arduinoData = serial.Serial('COM5', 9600)
sleep(2)

def mpu_writer():
    print(arduinoData.read_all().decode('utf-8'))
    num = input()  
    arduinoData.write(num.encode('utf-8'))
    arduinoData.write('\n'.encode('utf-8'))
    arduinoData.flushOutput()


def mpu_reader():
    while True:
        sleep(1)
        print(arduinoData.read_all().decode('utf-8'))
        


mpu_writer()
mpu_reader()