from mpd_connection import MPDConnection
from processing_metadata import process_metadata, join_metadata
from lastfm_api import LastFmMetadataGetter, LastFmApiException
from multiprocessing.managers import SyncManager
from multiprocessing import Event

# Shared objects
shared_song_metadata = {}
shared_mpd_status = {}
shared_playlist = {}
control_panel_new_song_event = Event()
control_panel_new_player_metadata_event = Event()
webapp_new_status_event = Event()

DEBUG_MODE = True


def initializer(self):
    server = self.manager.get_server()
    server.serve_forever()


class MetadataProvider:
    def __init__(self):
        # Set shared objects
        SyncManager.register('SharedSongMetadata', callable=lambda: shared_song_metadata)
        SyncManager.register('SharedMpdStatus', callable=lambda: shared_mpd_status)
        SyncManager.register('SharedPlaylist', callable=lambda: shared_playlist)
        SyncManager.register('ControlPanelNewSongEvent', callable=lambda: control_panel_new_song_event)
        SyncManager.register('ControlPanelNewPlayerMetadataEvent', callable=lambda: control_panel_new_player_metadata_event)
        SyncManager.register('WebappNewStatusEvent', callable=lambda: webapp_new_status_event)
        self.manager = SyncManager(address=('', 50000), authkey=b'abc')
        self.manager.start()
        self.song_metadata = self.manager.SharedSongMetadata()
        self.mpd_status = self.manager.SharedMpdStatus()
        self.current_playlist = self.manager.SharedPlaylist()
        self.webapp_new_status_event = self.manager.WebappNewStatusEvent()
        self.control_panel_new_song_event = self.manager.ControlPanelNewSongEvent()
        self.control_panel_new_player_metadata_event = self.manager.ControlPanelNewPlayerMetadataEvent()

        self.lastfm = LastFmMetadataGetter()
        self.mpd_connection = MPDConnection(host='localhost', port=6600,
                                            new_player_status_callback=self.new_player_status_callback,
                                            new_song_callback=self.new_song_callback,
                                            playlist_callback=self.playlist_change_callback)

    def new_song_callback(self):
        metadata_from_mpd = self.mpd_connection.get_current_song_metadata()
        processed_metadata = process_metadata(metadata_from_mpd)
        track = processed_metadata.get('track')
        artist = processed_metadata.get('artist')
        # album = processed_metadata.get('album')
        try:
            album_metadata, track_metadata = \
                self.lastfm.get_metadata(artist_name=artist, track_name=track)
        except LastFmApiException:
            track_metadata = {}
            album_metadata = {}
        joined_metadata = join_metadata(
            metadata_from_mpd=processed_metadata,
            track_metadata=track_metadata,
            album_metadata=album_metadata
        )
        self.song_metadata.update(joined_metadata)
        self.control_panel_new_song_event.set()
        # if DEBUG_MODE:
        # import pprint
        # pprint.pprint(joined_metadata)
        # print(joined_metadata)

    def new_player_status_callback(self):
        player_status = self.mpd_connection.get_player_status()
        self.mpd_status.update(player_status)
        self.webapp_new_status_event.set()
        self.control_panel_new_player_metadata_event.set()

    def playlist_change_callback(self):
        playlist = self.mpd_connection.get_playlist()
        self.current_playlist.update(playlist)
        self.webapp_new_status_event.set()


if __name__ == '__main__':
    prov = MetadataProvider()
    while 1:
        pass
