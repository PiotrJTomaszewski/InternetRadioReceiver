import serial
import select
from mpd_connection import MPDConnection

mpd_connection = None


class ButtonReader:
    def __init__(self):
        self.mpd_connection = MPDConnection('localhost', 6600)
        self.mpd_connection.connect()
        self.serial = serial.Serial(
            port='/dev/ttyS0',
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def reading_thread(self):
        serial_fd = self.serial.fileno()
        poller_object = select.poll()
        poller_object.register(serial_fd, select.POLLIN)
        callbacks = [self.button1_callback, self.button2_callback, self.button3_callback, self.button4_callback,
                     self.encoder_left_callback, self.encoder_right_callback, self.encoder_button_callback]
        while True:
            fd_event = poller_object.poll(10000000)
            for descriptor, _ in fd_event:
                received_value = self.serial.read()[0]
                for i in range(6, -1, -1):
                    current_bit = 1 << i
                    if received_value >= current_bit:
                        callbacks[i]()
                        received_value -= current_bit

    def button1_callback(self):
        print('button1')

    def button2_callback(self):
        print('button2')

    def button3_callback(self):
        print('button3')

    def button4_callback(self):
        print('button4')

    def encoder_right_callback(self):
        print('enc_right')

    def encoder_left_callback(self):
        print('enc_left')

    def encoder_button_callback(self):
        print('enc_button')
