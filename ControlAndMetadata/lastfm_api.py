import urllib.request
import json
from urllib.parse import quote_plus
from pprint import pprint
from collections import OrderedDict

DEBUG_MODE = True
# Globals
API_KEY_FILENAME = 'lastfm.key'
API_KEY_FILENAME = '../webapp/lastfm.key'
MAX_LOOKUP_SIZE = 50


class LastFmApiException(BaseException):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


class MetadataLookup(OrderedDict):
    """
    A lookup table to store metadata to limit LastFm API queries.
    Implements the LRU algorithm to limit the number of stored data.
    Code from an official Python documentation.
    """

    def __init__(self, max_size, *args, **kwds):
        self.maxsize = max_size
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class LastFmMetadataGetter:
    def __init__(self):
        with open(API_KEY_FILENAME) as api_key_file:
            api_key = api_key_file.readline()
            if api_key[-1] == '\n':
                self.api_key = api_key[:-1]
        self.api_url = 'http://ws.audioscrobbler.com/2.0'
        self.album_metadata_lookup = MetadataLookup(MAX_LOOKUP_SIZE)
        self.track_metadata_lookup = MetadataLookup(MAX_LOOKUP_SIZE)
        self.album_from_track_metadata_lookup = MetadataLookup(MAX_LOOKUP_SIZE)

    def get_metadata(self, artist_name, album_name=None, track_name=None):
        track_metadata = {}
        album_metadata = {}
        album_metadata_from_track = {}
        was_track_metadata_downloaded = False
        was_album_metadata_downloaded = False

        if artist_name is None:
            return album_metadata, track_metadata
        if track_name is not None:
            album_metadata_from_track, track_metadata, was_track_metadata_downloaded = \
                self._get_metadata_using_track_name(artist_name=artist_name, track_name=track_name)
        if album_name is None:
            album_name = album_metadata_from_track.get('album')
            print('LastFmApi: Using album name from track metadata - "{}"'.format(album_name))
        if album_name is not None:
            try:
                album_metadata, was_album_metadata_downloaded = \
                    self._get_metadata_using_album_name(artist_name=artist_name, album_name=album_name)
            except LastFmApiException:
                pass
        else:
            print('LastFmApi: Warning: Album name wasn\'t specified nor was it found in track metadata')
        if album_metadata is None or album_metadata == {}:
            album_metadata = album_metadata_from_track
        # If album metadata is missing cover url use one from track metadata
        elif album_metadata.get('cover_url') is None or album_metadata.get('cover_url') == '':
            album_metadata['cover_url'] = album_metadata_from_track.get('cover_url')
        # Save metadata in the lookup tables
        if was_album_metadata_downloaded:
            if album_metadata is not None and album_metadata != {}:
                if album_name is not None and album_name != '':
                    print('LastFmApi: Saving album metadata in the lookup table')
                    self.album_metadata_lookup[artist_name + '/' + album_name] = album_metadata
        if was_track_metadata_downloaded:
            if track_metadata is not None and track_metadata != {}:
                if track_name is not None and track_name != '':
                    print('LastFmApi: Saving track metadata in the lookup table')
                    self.track_metadata_lookup[artist_name + '/' + track_name] = track_metadata
            if album_metadata_from_track is not None and album_metadata_from_track != {}:
                if track_name is not None and track_name != '':
                    print('LastFmApi: Saving album from track metadata in the lookup table')
                    self.album_from_track_metadata_lookup[artist_name + '/' + track_name] = album_metadata_from_track
        return album_metadata, track_metadata

    def _get_metadata_using_album_name(self, artist_name, album_name):
        if artist_name is None or album_name is None:
            return {}, False
        # Check if metadata is already present in the lookup table
        album_metadata = self.album_metadata_lookup.get(artist_name + '/' + album_name)
        if album_metadata is not None:
            print('LastFmApi: Found metadata in the lookup table for album "{}" by "{}"'.format(
                album_name, artist_name))
            return album_metadata, False
        # Download metadata
        album_metadata = self._download_metadata_using_album_name(artist_name=artist_name, album_name=album_name)
        return album_metadata, True

    def _get_metadata_using_track_name(self, artist_name, track_name):
        album_metadata_from_track = {}
        track_metadata = {}
        if artist_name is None or track_name is None:
            return album_metadata_from_track, track_metadata, False
        # Check if metadata is already present in the lookup table
        track_metadata = self.track_metadata_lookup.get(artist_name + '/' + track_name)
        album_metadata_from_track = self.album_from_track_metadata_lookup.get(artist_name + '/' + track_name)
        if track_name is not None and album_metadata_from_track is not None:
            print('LastFmApi: Found metadata in the lookup table for track "{}" by "{}"'.format(
                track_name, artist_name))
            return album_metadata_from_track, track_metadata, False
        # Download metadata
        album_metadata_from_track, track_metadata = self._download_metadata_using_track_name(artist_name, track_name)
        return album_metadata_from_track, track_metadata, True

    def _download_metadata_using_album_name(self, artist_name, album_name, enable_autocorrect=0):
        if DEBUG_MODE:
            print('LastFmApi: Downloading metadata for album "{}" by "{}"'.format(album_name, artist_name))
        # Convert the strings to a format acceptable in URLs
        artist_name_encoded = quote_plus(artist_name)
        album_name_encoded = quote_plus(album_name)
        response = urllib.request.urlopen(
            self.api_url +
            '/?method=album.getinfo&api_key={key}&artist={artist}&album={album}&autocorrect={autocorrect}&format=json'
            .format(
                key=self.api_key, artist=artist_name_encoded, album=album_name_encoded, autocorrect=enable_autocorrect
            )).read()
        decoded_response = json.loads(response)
        # Handle errors
        if decoded_response.get('error') is not None:
            raise LastFmApiException("""An error occurred while trying to receive data from lastFm API.
                        Error number: {}, 
                        Error message: {}""".format(decoded_response.get('error'), decoded_response.get('message')))

        album = decoded_response.get('album')
        # pprint(decoded_response)
        album_metadata = {'artist': artist_name, 'album': album_name}
        if album.get('image') is not None:
            album_metadata['cover_url'] = album.get('image')[-1].get('#text')
        if album.get('wiki') is not None:
            album_metadata['wiki'] = album.get('wiki').get('content')
            album_metadata['wiki_summary'] = album.get('wiki').get('summary')
        if album.get('tags') is not None:
            album_metadata['tags'] = album.get('tags').get('tag')
        if album.get('tracks') is not None:
            tracklist = album.get('tracks').get('track')
            tracklist_titles = [track.get('name') for track in tracklist]  # Get only names of the songs
            album_metadata['tracklist'] = tracklist_titles
        return album_metadata

    def _download_metadata_using_track_name(self, artist_name, track_name, enable_autocorrect=0):
        """

        :param artist_name:
        :param track_name:
        :param enable_autocorrect:
        :return:
        """
        if DEBUG_MODE:
            print('LastFmApi: Downloading metadata for track "{}" by "{}"'.format(track_name, artist_name))
        # Convert the strings to a format acceptable in URLs
        artist_name_encoded = quote_plus(artist_name)
        track_name_encoded = quote_plus(track_name)
        response = urllib.request.urlopen(
            self.api_url +
            '/?method=track.getInfo&api_key={key}&artist={artist}&track={track}&autocorrect={autocorrect}&format=json'
            .format(
                key=self.api_key, artist=artist_name_encoded, track=track_name_encoded, autocorrect=enable_autocorrect
            )).read()
        decoded_response = json.loads(response)
        # pprint(decoded_response)
        # Handle errors
        if decoded_response.get('error') is not None:
            raise LastFmApiException("""An error occurred while trying to receive data from lastFm API.
                    Error number: {}, 
                    Error message: {}""".format(decoded_response.get('error'), decoded_response.get('message')))
        track_metadata = {'artist': artist_name, 'track': track_name}
        album_metadata = {'artist': artist_name}
        track = decoded_response.get('track')
        if track.get('toptags') is not None:
            track_metadata['tags'] = track.get('toptags').get('tag')
        if track.get('wiki') is not None:
            track_metadata['wiki'] = track.get('wiki').get('content')
            track_metadata['wiki_summary'] = track.get('wiki').get('summary')
        album = track.get('album')
        if album is not None:
            album_name = album.get('title')
            album_metadata['album'] = album_name
            if album.get('image') is not None:
                album_metadata['cover_url'] = album.get('image')[-1].get('#text')
        else:
            if DEBUG_MODE:
                print('LastFmApi: Warning, no album metadata found')
        return album_metadata, track_metadata


if __name__ == '__main__':
    lastfm = LastFmMetadataGetter()
    pprint(lastfm.get_metadata(artist_name='Hammerfall', album_name='Built to last'))
    pprint(lastfm.get_metadata(artist_name='Hammerfall', album_name='Built to last'))
    pprint(lastfm.get_metadata(artist_name='Metallica', album_name='Master of Puppets'))
    pprint(lastfm.get_metadata(artist_name="Hammerfall", track_name='Any Means Necessary'))
    pprint(lastfm.get_metadata(artist_name='Hammerfall', album_name='No Sacrifice, No Victory'))

# TODO: Artist name like U.D.O not warking, titles like Rockin' Around the Xmas Tree
