from math import acos, sqrt
from time import sleep

import serial
import serial.tools.list_ports
from serial.serialutil import SerialException, SerialTimeoutException, Timeout


class SerialIO():
    def __init__(self):
        self.setup()
        self.list_dir_mode()

        # self.ard_dump_mode()

    def setup(self):
        ports = list(serial.tools.list_ports.comports())
        self.arduino_data = None
        print(ports)
        # Procura pelo Arduino conectado:
        for p in ports:
            print(p)
            if 'USB-SERIAL CH340' in p.description:
                try:
                    self.arduino_data = serial.Serial(p.name, 9600, timeout=1)
                    print('Arduino encontrado!')
                except Exception:
                    print('Porta Serial Arduino ocupada!')
                    exit()

        if not self.arduino_data:
            print('Arduino não encontrado!')
            exit()

        sleep(2)

        # self.arduino_data.write(('#\n\r'.encode('utf-8'))

    def get_integer_value(self, str_value):
        if str_value.startswith('+'):
            return int(str_value[1:])
        else:
            return int(str_value)

    def get_x_y_z_dump(self, input_str):
        # Retira o primeiro e os quatro últimos elementos da linha
        var_list = input_str.split(' ')[1:][:-3]
        if len(var_list) == 0:
            return 0, 0, 0
        x, y, z = [self.get_integer_value(value) for value in var_list]
        return x, y, z

    def get_temp_dump(self, input_str):
        return self.get_integer_value(input_str.split(' ')[4])

    def get_bat_tension_dump(self, input_str):
        return self.get_integer_value(input_str.split(' ')[5])

    def real_time_read(self):
        reference_vector = None
        current_vector = None
        while True:
            normalized_buffer = self.arduino_data.read_until().decode('utf-8')
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
        except Exception:
            angulo = 0
        return round(angulo, 0)

    def ard_dump_mode(self, beer):
        # Forçando modo 17 (Config Mode)
        self.arduino_data.write('17\n'.encode('utf-8'))
        self.arduino_data.flushOutput()
        # Printando dados do primeiro diretório
        self.arduino_data.write(
            ('p ' + str(beer.index) + '\n').encode('utf-8'))
        self.arduino_data.flushOutput()
        self.save_dump(beer.name)

    def save_dump(self, beer_name):
        with open(beer_name + '_dump.txt', 'w') as f:
            while True:
                buffer = self.serial_read()
                if '#[f' in buffer:
                    while True:
                        buffer = self.serial_read()
                        if not 'f]#' in buffer:
                            f.write(buffer + '\n')
                        else:
                            break
                    self.voltar_menu_serial()
                    f.close()
                    return

    def list_dir_mode(self):
        # Forçando modo 17 (Config Mode)
        self.arduino_data.write('17\n'.encode('utf-8'))
        self.arduino_data.flushOutput()

        # Printando todos diretórios ocupados
        self.arduino_data.write('l\n'.encode('utf-8'))
        self.arduino_data.flushOutput()

        self.save_directories()

    def save_directories(self):
        with open('directories.txt', 'w') as f:
            while True:
                # Ler linha a linha,  Decodificação para incluir \n, \r
                buffer = self.serial_read()
                if 'Dir:' in buffer:  # Primeira medida do dump
                    while buffer:
                        buffer = self.serial_read()
                        if buffer:
                            f.write(buffer + '\n')
                    self.voltar_menu_serial()
                    f.close()
                    return

    def serial_read(self):
        try:
            buffer = self.arduino_data.readline().decode('ISO-8859-1')
        except Exception:
            buffer = None
        return buffer.rstrip()

    def vector_read(self, buffer):
        if 'FFFF' in buffer:  # Critério de parada (último índice)
            raise Exception
        else:
            return self.get_x_y_z_dump(buffer)

    def get_angle_list(self, beer):
        angle_list = list()
        buffer = ''
        with open(beer + '_dump.txt', 'r') as f:
            while not '0004' in buffer:
                buffer = f.readline()
            ref_vector = self.vector_read(buffer)
            while True:
                try:
                    buffer = f.readline()
                    angle_list.append(
                        self.angle_calc(ref_vector, self.vector_read(buffer)))
                except Exception:
                    break
            f.close()
        return angle_list

    def get_directories(self):
        dir_list = list()
        with open('directories.txt', 'r') as f:
            for idx, line in enumerate(f, start=0):
                beer = Beer(idx, line.split()[1])
                dir_list.append(beer)
            f.close()
        return dir_list

    def get_tension_list(self, beer):
        tension_list = list()
        buffer = ''
        with open(beer + '_dump.txt', 'r') as f:
            while not '0004' in buffer:
                buffer = f.readline()
            while True:
                try:
                    tension = self.get_bat_tension_dump(buffer)
                    tension_list.append(tension)
                    buffer = f.readline()
                    if 'FFFF' in buffer:
                        break
                except Exception:
                    break
            f.close()
        return tension_list

    def get_temp_list(self, beer):
        temp_list = list()
        buffer = ''
        with open(beer + '_dump.txt', 'r') as f:
            while not '0004' in buffer:
                buffer = f.readline()
            while True:
                try:
                    temp = self.get_temp_dump(buffer)
                    temp_list.append(temp)
                    buffer = f.readline()
                    if 'FFFF' in buffer:
                        break
                except Exception:
                    break
            f.close()
        return temp_list

    def voltar_menu_serial(self):
        self.arduino_data.write('x\n'.encode('utf-8'))
        self.arduino_data.flushOutput()
        return


class Beer(object):
    index = 0
    name = ''

    def __init__(self, index, name):
        self.index = index
        self.name = name


if __name__ == "__main__":
    SerialIO()
