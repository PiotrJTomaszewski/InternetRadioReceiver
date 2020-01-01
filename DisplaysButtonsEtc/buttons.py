import serial
import select
import threading

mpd_connection = None


class ButtonReader:
    def __init__(self, callbacks):
        self.serial = serial.Serial(
            port='/dev/ttyS0',
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        # Assign callbacks
        self.button1_callback = callbacks['button1']
        self.button2_callback = callbacks['button2']
        self.button3_callback = callbacks['button3']
        self.button4_callback = callbacks['button4']
        self.encoder_left_callback = callbacks['encoder_left']
        self.encoder_right_callback = callbacks['encoder_right']
        self.encoder_button_callback = callbacks['encoder_button']
        self.reading_thread = threading.Thread(target=self.reading_thread_function)

    def reading_thread_function(self):
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

    def start_reading_thread(self):
        self.reading_thread.start()
