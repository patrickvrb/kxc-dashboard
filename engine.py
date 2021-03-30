from math import acos, sqrt
from time import sleep

import serial
import serial.tools.list_ports
from serial.serialutil import SerialException, SerialTimeoutException, Timeout


class SerialIO():
    def __init__(self):
        self.setup()

    def setup(self):

        ports = list(serial.tools.list_ports.comports())

        # Procura pelo Arduino conectado:
        for p in ports:
            if 'USB-SERIAL CH340' in p.description:
                print('Arduino encontrado!')
                self.arduinoData = serial.Serial(p.name, 9600, timeout=1)

        sleep(2)

        # mode = input('Modo? 0 para Real Time e 1 para Catch Dump\t')
        # mode = '1'
        # if(mode == '0'):
        #     self.real_time_read()
        # elif (mode == '1'):
        #   self.ard_dump_mode()
        # else:
        #     print('Modo não existente')

    def get_integer_value(self, str_value):
        if str_value.startswith('+'):
            return int(str_value[1:])
        else:
            return int(str_value)

    def get_x_y_z(self,  input_str):
        var_list = input_str.split(' ')
        x, y, z = [self.get_integer_value(value) for value in var_list]
        return x, y, z

    def get_x_y_z_dump(self, input_str):
        # Retira o primeiro e os quatro últimos elementos da linha
        var_list = input_str.split(' ')[1:][:-4]
        if len(var_list) == 0:
            return 0, 0, 0
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
                    angulo = self.angle_calc(reference_vector, current_vector)
                    print(round(angulo, 0))

    def angle_calc(self, ref_vector, vector):
        try:
            produto_interno = sum([vector[i] * ref_vector[i]
                                  for i in range(3)])
            u = sqrt(sum([vector[i] * vector[i] for i in range(3)]))
            v = sqrt(sum([ref_vector[i] * ref_vector[i] for i in range(3)]))
            angulo = acos(produto_interno/(u*v)) * 57.3
        except ValueError:
            angulo = 0
        except ZeroDivisionError:
            angulo = 0
        return int(round(angulo, 0))

    def ard_dump_mode(self):
        # Forçando modo 17 (Config Mode)
        self.arduinoData.write('17'.encode('utf-8'))
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()
        sleep(2)
        # Printando dados do primeiro diretório
        self.arduinoData.write('p 0'.encode('utf-8'))
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()
        sleep(1)
        self.catch_dump()

    def list_dir_mode(self):
        # Forçando modo 17 (Config Mode)
        self.arduinoData.write('17'.encode('utf-8'))
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()

        # Printando todos diretórios ocupados
        self.arduinoData.write('l'.encode('utf-8'))
        self.arduinoData.write('\n'.encode('utf-8'))
        self.arduinoData.flushOutput()
        self.save_directories()
        return

    def save_directories(self):
        with open('directories.txt', 'w') as f:
            while True:
                # Ler linha a linha,  Decodificação para incluir \n, \r
                buffer = self.serial_dir_read()
                if buffer.startswith('Dir:'):  # Primeira medida do dump
                    while buffer:
                        buffer = self.serial_dir_read()
                        if buffer:
                            f.write(buffer + '\n')
                        print(buffer)
                    f.close()
                    return

    def serial_dir_read(self):
        try:
            buffer = self.arduinoData.readline().decode('ISO-8859-1')
        except SerialTimeoutException:
            buffer = None
        except EOFError:
            buffer = None
        return buffer.rstrip()

    def serial_vector_read(self):
        data = self.arduinoData.read_until().decode('ISO-8859-1')
        if 'FFFF' in data:  # Critério de parada (último índice)
            raise EOFError
        else:
            return self.get_x_y_z_dump(data)

    def catch_dump(self):
        with open('flash_dump.txt', 'w') as f:
            while True:
                sleep(.1)
                # Ler linha a linha,  Decodificação para incluir \n, \r
                serial_buffer = self.arduinoData.read_until().decode('ISO-8859-1')
                if serial_buffer.startswith('0003'):  # Primeira medida do dump
                    while True:
                        try:
                            current_vector = self.serial_vector_read()
                            f.write(str(current_vector) + '\n')
                            # print(current_vector)
                        except EOFError:
                            break
                        except SerialTimeoutException:
                            break
                    f.close()
                    return

    def get_angle_list(self):
        angle_list = list()
        with open('flash_dump.txt', 'r') as f:
            ref_vector = self.get_x_y_z(f.readline().rstrip().replace(
                '(', '').replace(')', '').replace(',', ''))
            while True:
                values = f.readline().rstrip().replace(
                    '(', '').replace(')', '').replace(',', '')
                if values:
                    curr_vector = self.get_x_y_z(values)
                else:
                    break
                angle_list.append(self.angle_calc(ref_vector, curr_vector))
            f.close()
        return angle_list


if __name__ == "__main__":
    SerialIO()
