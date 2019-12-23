from mpd import MPDClient, base
DEBUG_MODE = True


class SeriousConnectionError(BaseException):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


def reconnect_on_failure(func):
    def try_and_reconnect(self, *args, **kwargs):
        number_of_tries = 0
        while number_of_tries < 3:
            try:
                number_of_tries += 1
                result = func(self, *args, **kwargs)
                return result
            except base.ConnectionError:
                self.connect()
                if DEBUG_MODE:
                    print('MPD_CLIENT: Connection to mpd lost. Reconnecting')
        raise SeriousConnectionError('Error: Maximum numbers of connection to MPD tries reached!')
    return try_and_reconnect


class MPDConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = MPDClient()

    def __del__(self):
        self.client.disconnect()

    def connect(self):
        self.client.connect(self.host, self.port)

    @reconnect_on_failure
    def get_volume(self):
        return self.client.status().get('volume')

    @reconnect_on_failure
    def change_volume(self, vol_difference):
        current_volume = self.get_volume()
        new_volume = current_volume + vol_difference
        # Volume should be between 0 and 100
        if new_volume < 0:
            new_volume = 0
        elif new_volume > 100:
            new_volume = 100
        self.client.setvol(new_volume)

    @reconnect_on_failure
    def pause(self):
        self.client.pause(1)

    @reconnect_on_failure
    def play(self):
        self.client.play(0)

    @reconnect_on_failure
    def prev(self):
        self.client.prev()

    @reconnect_on_failure
    def next(self):
        self.client.previous()
