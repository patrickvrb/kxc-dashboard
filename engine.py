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
                print('Arduino encontrado!')
                self.arduino_data = serial.Serial(p.name, 9600, timeout=1)

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
        except:
            angulo = 0

        return int(round(angulo, 0))

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
        with open(str(beer_name) + '_dump.txt', 'w') as f:
            # f.write(beer_name + '\n')
            while True:
                # Ler linha a linha,  Decodificação para incluir \n, \r
                serial_buffer = self.arduino_data.read_until().decode('ISO-8859-1')
                if serial_buffer.startswith('0003'):  # Primeira medida do dump
                    while True:
                        try:
                            current_vector = self.serial_vector_read()
                            f.write(str(current_vector) + '\n')
                        except:
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
                buffer = self.serial_dir_read()
                if buffer.startswith('Dir:'):  # Primeira medida do dump
                    while buffer:
                        buffer = self.serial_dir_read()
                        if buffer:
                            f.write(buffer + '\n')
                        print(buffer)
                    self.voltar_menu_serial()
                    f.close()
                    return

    def serial_dir_read(self):
        try:
            buffer = self.arduino_data.readline().decode('ISO-8859-1')
        except:
            buffer = None
        return buffer.rstrip()

    def serial_vector_read(self):
        data = self.arduino_data.read_until().decode('ISO-8859-1')
        if 'FFFF' in data:  # Critério de parada (último índice)
            raise EOFError
        else:
            return self.get_x_y_z_dump(data)

    def get_angle_list(self, beer):
        angle_list = list()
        with open(str(beer) + '_dump.txt', 'r') as f:
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
            self.voltar_menu_serial()
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
