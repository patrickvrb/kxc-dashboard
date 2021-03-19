import sys
from math import acos, sqrt
from time import sleep

import serial
from PyQt5 import QtWidgets

from dashboard import MainWindow


class SerialIO():
    def __init__(self):
        self.setup()

    def setup(self):
        self.arduinoData = serial.Serial('COM5', 9600)
        sleep(2)
        # mode = input('Modo? 0 para Real Time e 1 para Catch Dump\t')
        mode = '1'
        if(mode == '0'):
            self.real_time_read()
        elif (mode == '1'):
            self.ard_dump_mode()
        else:
            print('Modo não existente')
    
    def get_integer_value(self, str_value):
        if str_value.startswith('+'):
            return int(str_value[1:])
        else:
            return int(str_value)

    def get_x_y_z(self,  input_str):
        var_list = input_str.split(' ')[:-1]
        x, y, z = [self.get_integer_value(value) for value in var_list]
        return x, y, z
    
    def get_x_y_z_dump(self, input_str):
        var_list = input_str.split(' ')[1:][:-4] # Retira o primeiro e os quatro últimos elementos da linha
        x, y, z = [self.get_integer_value(value) for value in var_list]
        return x, y, z
    
    def real_time_read(self):
        reference_vector = None
        current_vector = None
        while True:
            normalized_buffer = self.arduinoData.read_until().decode('utf-8')
            if not normalized_buffer.startswith('==>'):    
                x, y, z = self.get_x_y_z(normalized_buffer)
                current_vector = [x, y, z]
                if reference_vector is None:
                    reference_vector = current_vector
                if current_vector and reference_vector:
                    try:
                        produto_interno = sum([current_vector[i] * reference_vector[i] for i in range(3)])
                        u = sqrt(sum([current_vector[i] * current_vector[i] for i in range(3)]))
                        v = sqrt(sum([reference_vector[i] * reference_vector[i] for i in range(3)]))
                        angulo = acos(produto_interno/(u*v)) * 57.3 
                    except ValueError: 
                        angulo = 0
                    print(round(angulo, 0))
                    
    def ard_dump_mode(self):
        self.arduinoData.write('17'.encode('utf-8')) # Forçando modo 17 (Config Mode)
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()
        sleep(2)
        self.arduinoData.write('p 0'.encode('utf-8')) # Printando dados do primeiro diretório
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()
        sleep(1)
        self.catch_dump()
        
                    
    def catch_dump(self):
        with open('flash_dump.txt', 'w+') as f:
            while True:
                sleep(.1)
                serial_buffer = self.arduinoData.read_until().decode('ISO-8859-1') # Ler linha a linha,  Decodificação para incluir \n, \r
                if serial_buffer.startswith('0003'): # Primeira medida do dump
                    while not 'FFFF' in serial_buffer: # Critério de parada (último índice)
                        serial_buffer = self.arduinoData.read_until().decode('ISO-8859-1') 
                        x, y, z = self.get_x_y_z_dump(serial_buffer)
                        f.write(str([x, y, z]) + '\n')
                        print(str([x, y, z]))
                    f.close()
                    sys.exit()
           
            
                

if __name__ == "__main__":
    SerialIO()
