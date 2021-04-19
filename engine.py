from math import acos, sqrt
from time import sleep

import serial
import serial.tools.list_ports
from serial.serialutil import SerialException, SerialTimeoutException, Timeout


class SerialIO():
    def __init__(self):
        self.setup()
        self.list_dir_mode()

    def setup(self):
        ports = list(serial.tools.list_ports.comports())
        self.arduino_data = None
        # Procura pelo Arduino conectado:
        for p in ports:
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
        temp = self.get_integer_value(input_str.split(' ')[4]) / 10
        if temp < 0 or temp > 50:
            return self.prev_temp
        else:
            self.prev_temp = temp
            return temp

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
        self.save_dump(beer.name[0])

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
                    return

    def get_directories(self):
        dir_list = list()
        with open('directories.txt', 'r') as f:
            for idx, line in enumerate(f, start=0):
                beer = Beer(idx, line.split()[
                            1] + ' - ' + line.split()[2] + ' - ' + line.split()[3])
                dir_list.append(beer)
        return dir_list

    def serial_read(self):
        try:
            buffer = self.arduino_data.readline().decode('ISO-8859-1')
        except Exception:
            buffer = None
        return buffer.rstrip()

    def get_measures_lists(self, beer):
        tension_list = list()
        temp_list = list()
        angle_list = list()
        coord_list = list()
        buffer = ''
        with open(beer.name[0] + '_dump.txt', 'r') as f:
            while buffer[:4] != '0004':
                buffer = f.readline()
            ref_vector = self.get_x_y_z_dump(buffer)
            while True:
                try:
                    tension = self.get_bat_tension_dump(buffer)
                    tension_list.append(tension)

                    temp = self.get_temp_dump(buffer)
                    temp_list.append(temp)

                    vector = self.get_x_y_z_dump(buffer)
                    angle_list.append(self.angle_calc(ref_vector, vector))

                    coord_list.append(self.get_x_y_z_dump(buffer))

                    buffer = f.readline()
                    if buffer[:4] == 'FFFF':
                        break
                except Exception:
                    break
        return tension_list, temp_list, angle_list, coord_list

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
