from math import acos, sqrt
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
    
    def get_integer_value(self, str_value):
        if str_value.startswith('+'):
            return int(str_value[1:])
        else:
            return int(str_value)

    def get_x_y_z(self,  input_str):
        var_list = input_str.split(' ')[:-1]
        x, y, z = [self.get_integer_value(value) for value in var_list]
        return x, y, z

    def read(self):
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
                    print(round(angulo, 2))
        
                

if __name__ == "__main__":
    SerialIO().read()