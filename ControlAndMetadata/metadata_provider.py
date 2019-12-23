from mpd_connection import MPDConnection
from processing_metadata import process_metadata, join_metadata
from lastfm_api import LastFmMetadataGetter, LastFmApiException
from multiprocessing.managers import SyncManager
from threading import Event
from multiprocessing import Queue

# Shared objects
shared_song_metadata = {}
shared_mpd_status = {}

DEBUG_MODE = True


def get_shared_song_metadata():
    return shared_song_metadata


def get_shared_mpd_status():
    return shared_mpd_status


def initializer(self):
    server = self.manager.get_server()
    server.serve_forever()


class MetadataProvider:
    def __init__(self):
        # Set shared objects
        SyncManager.register('SharedSongMetadata', callable=get_shared_song_metadata)
        SyncManager.register('SharedMpdStatus', callable=get_shared_mpd_status)
        self.manager = SyncManager(address=('', 50000), authkey=b'abc')
        self.manager.start()
        self.song_metadata = self.manager.SharedSongMetadata()
        self.mpd_status = self.manager.SharedMpdStatus()

        self.lastfm = LastFmMetadataGetter()
        self.mpd_connection = MPDConnection(host='localhost', port=6600,
                                            new_player_status_callback=self.new_player_status_callback,
                                            new_song_callback=self.new_song_callback)

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
        # if DEBUG_MODE:
            # import pprint
            # pprint.pprint(joined_metadata)
            # print(joined_metadata)

    def new_player_status_callback(self):
        player_status = self.mpd_connection.get_player_status()
        self.mpd_status.update(player_status)


if __name__ == '__main__':
    prov = MetadataProvider()
    while 1:
        pass
