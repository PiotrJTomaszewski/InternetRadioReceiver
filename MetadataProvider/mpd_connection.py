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
    def __init__(self, host, port, new_player_status_callback, new_song_callback, playlist_callback):
        self.host = host
        self.port = port
        self.active_client = MPDClient()
        self.idling_client = MPDClient()
        self.new_player_status_callback = new_player_status_callback
        self.new_song_callback = new_song_callback
        self.playlist_callback = playlist_callback
        self.idling_thread = threading.Thread(target=self._start_idling_client, daemon=True)
        self.idling_thread.start()
        self.player_status = {}
        self.current_song_metadata = {}
        self.last_song_title = ""
        self.current_playlist = {}
        self.last_playlist_length = 0

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

    def get_playlist(self):
        return self.current_playlist

    @reconnect_on_failure(client='active')
    def update_player_status(self):
        self.player_status = self.active_client.status()

    @reconnect_on_failure(client='active')
    def update_playlist(self):
        self.current_playlist = self.active_client.playlistid()

    def get_player_status(self):
        return self.player_status

    @reconnect_on_failure(client='active')
    def update_current_song_metadata(self):
        self.current_song_metadata = self.active_client.currentsong()

    def get_current_song_metadata(self):
        return self.current_song_metadata

    def player_state(self):
        return self.player_status.get('state')

    @reconnect_on_failure(client='idling')
    def idle(self):
        return self.idling_client.idle()

    def _handle_player_event(self):
        print('MPD_CLIENT: New player status')
        self.update_player_status()
        self.new_player_status_callback()
        self.update_current_song_metadata()
        # Check if there is a new song
        if self.current_song_metadata.get('title') != self.last_song_title:
            if DEBUG_MODE:
                print('MPD_CLIENT: New song')
            self.new_song_callback()
        self.last_song_title = self.current_song_metadata.get('title')

    def _handle_mixer_event(self):
        print('MPD_CLIENT: New player status')
        self.update_player_status()
        self.new_player_status_callback()

    def _handle_playlist_event(self):
        if self.last_playlist_length != len(self.get_playlist()):
            print('MPD_CLIENT: Playlist has changed')
            self.update_playlist()
            self.playlist_callback()
            self.last_playlist_length = len(self.get_playlist())

    def _start_idling_client(self):
        self.connect_idling_client()
        if DEBUG_MODE:
            print('MPD_CLIENT: Starting idling thread')
        self.update_player_status()
        self.update_current_song_metadata()
        self.new_player_status_callback()
        self.new_song_callback()
        self.last_song_title = self.current_song_metadata.get('title')
        self.update_playlist()
        self.last_playlist_length = len(self.get_playlist())
        while True:
            # Wait for a signal from server
            events = self.idle()
            for event in events:
                if event == 'player':
                    self._handle_player_event()
                elif event == 'mixer':
                    self._handle_mixer_event()
                elif event == 'playlist':
                    self._handle_playlist_event()


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
