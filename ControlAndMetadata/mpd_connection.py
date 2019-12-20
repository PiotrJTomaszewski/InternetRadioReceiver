from mpd import MPDClient, base

DEBUG_MODE = True

# Globals
mpd_connection_parameters = {}
mpd_client = None


def mpd_init(host, port):
    global mpd_client
    mpd_client = MPDClient()
    mpd_connection_parameters['host'] = host
    mpd_connection_parameters['port'] = port


class SeriousConnectionError(BaseException):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


def reconnect_on_failure(func, *args, **kwargs):
    def try_and_reconnect():
        number_of_tries = 0
        while number_of_tries < 3:
            try:
                number_of_tries += 1
                result = func(*args, **kwargs)
                return result
            except base.ConnectionError:
                if DEBUG_MODE:
                    print('Connection to mpd lost. Reconnecting')
        raise SeriousConnectionError('Error: Maximum numbers of connection to MPD tries reached!')

    return try_and_reconnect


def mpd_connect():
    mpd_client.connect(mpd_connection_parameters['host'], mpd_connection_parameters['port'])


@reconnect_on_failure
def mpd_get_playlist():
    return mpd_client.playlistid()


@reconnect_on_failure
def mpd_get_current_song():
    return mpd_client.currentsong()


if __name__ == '__main__':
    mpd_init('localhost', 6600)
    mpd_connect()
    print(mpd_get_playlist())
    print(mpd_get_current_song())
