from mpd import MPDClient, base
import threading

DEBUG_MODE = True


class SeriousConnectionError(BaseException):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


def reconnect_on_failure(client):
    def decorator(func):
        def try_and_reconnect(self, *args, **kwargs):
            number_of_tries = 0
            while number_of_tries < 3:
                try:
                    number_of_tries += 1
                    result = func(self, *args, **kwargs)
                    return result
                except base.ConnectionError:
                    if client == 'active':
                        self.connect_active_client()
                    else:
                        self.connect_idling_client()
                    if DEBUG_MODE:
                        print('MPD_CLIENT: Connection to mpd lost. Reconnecting')
            raise SeriousConnectionError('Error: Maximum numbers of connection to MPD tries reached!')

        return try_and_reconnect

    return decorator


class MPDConnection:
    def __init__(self, host, port, new_player_status_callback, new_song_callback):
        self.host = host
        self.port = port
        self.active_client = MPDClient()
        self.idling_client = MPDClient()
        self.new_player_status_callback = new_player_status_callback
        self.new_song_callback = new_song_callback
        self.idling_thread = threading.Thread(target=self._start_idling_client, daemon=True)
        self.idling_thread.start()
        self.player_status = {}
        self.current_song_metadata = {}

    def __del__(self):
        # TODO: Kill idling thread
        self.idling_client.disconnect()
        self.active_client.disconnect()

    def connect(self, client):
        client.connect(self.host, self.port)

    def connect_active_client(self):
        self.active_client.connect(self.host, self.port)

    def connect_idling_client(self):
        self.idling_client.connect(self.host, self.port)

    @reconnect_on_failure(client='active')
    def get_playlist(self):
        return self.active_client.playlistid()

    @reconnect_on_failure(client='active')
    def update_player_status(self):
        self.player_status = self.active_client.status()

    def get_player_status(self):
        return self.player_status

    @reconnect_on_failure(client='active')
    def update_current_song_metadata(self):
        self.current_song_metadata = self.active_client.currentsong()

    def get_current_song_metadata(self):
        return self.current_song_metadata

    # def get_volume(self):
    #     return self.player_status.get('volume')

    # @reconnect_on_failure(client='active')
    # def pause(self):
    #     self.active_client.pause(1)
    #
    # @reconnect_on_failure(client='active')
    # def play(self):
    #     self.active_client.play(0)

    def player_state(self):
        return self.player_status.get('state')

    @reconnect_on_failure(client='idling')
    def idle(self):
        return self.idling_client.idle()

    def _start_idling_client(self):
        self.connect_idling_client()
        if DEBUG_MODE:
            print('MPD_CLIENT: Starting idling thread')
        self.update_player_status()
        self.update_current_song_metadata()
        self.new_player_status_callback()
        self.new_song_callback()
        last_song_title = self.current_song_metadata.get('title')
        while True:
            # Wait for a change in player status
            events = self.idle()
            noteworthy_event = False
            for event in events:
                if event in ('player', 'mixer'):
                    noteworthy_event = True
                    break
            if not noteworthy_event:
                # If nothing important has happened
                continue
            if DEBUG_MODE:
                print('MPD_CLIENT: New player status')
            # Get status from player
            self.update_player_status()
            self.update_current_song_metadata()
            self.new_player_status_callback()
            # Check if there is a new song
            if self.current_song_metadata.get('title') != last_song_title:
                if DEBUG_MODE:
                    print('MPD_CLIENT: New song')
                self.new_song_callback()
            last_song_title = self.current_song_metadata.get('title')


if __name__ == '__main__':
    def a():
        pass


    # mpd_init('localhost', 6600)
    # mpd_connect(mpd_idling_client)
    mpd_connection = MPDConnection('localhost', 6600, a, a)
    # print(mpd_connection.get_playlist())
    import time

    time.sleep(1)
    print(mpd_connection.get_player_status())
    while 1:
        pass
