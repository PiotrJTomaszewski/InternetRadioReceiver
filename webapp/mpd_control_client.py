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


class MPDControlClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = MPDClient()
        # TODO: the format should be m3u
        self.stations_file_name = 'radio_stations'

    def __del__(self):
        # TODO: Kill idling thread
        self.client.disconnect()

    def connect(self):
        self.client.connect(self.host, self.port)

    @reconnect_on_failure
    def get_stations(self):
        return self.client.playlistid()

    @reconnect_on_failure
    def get_volume(self):
        return self.client.get('volume')

    @reconnect_on_failure
    def change_volume(self, value=5):
        current_volume = self.get_volume()
        new_volume = current_volume + value
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0
        return self.client.setvol(new_volume)

    def increase_volume(self, value=5):
        return self.change_volume(value)

    def decrease_volume(self, value=5):
        return self.change_volume(-value)

    @reconnect_on_failure
    def pause(self):
        self.client.pause(1)

    @reconnect_on_failure
    def play(self):
        self.client.play(0)

    @reconnect_on_failure
    def prev(self):
        self.client.previous()

    @reconnect_on_failure
    def next(self):
        self.client.next()

    @reconnect_on_failure
    def switch_to_station(self, station_id):
        self.client.playid(station_id)

    @reconnect_on_failure
    def save_stations(self):
        self.client.save(self.stations_file_name)


if __name__ == '__main__':
    pass
