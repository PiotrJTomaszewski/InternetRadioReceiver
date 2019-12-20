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

    def get_metadata(self, artist_name, album_name=None, track_name=None):
        track_metadata = None
        album_metadata = None
        if album_name is not None:
            album_metadata = self.album_metadata_lookup.get(artist_name + '/' + album_name)
            if album_metadata is None:  # If there is no metadata stored then download it
                if DEBUG_MODE:
                    print('LastFmApi: Metadata for album "{}" by "{}" not found. Downloading it using album name.'
                          .format(album_name, artist_name))
                self._get_metadata_using_album_name(artist_name, album_name)
            elif DEBUG_MODE:
                print('LastFmApi: Metadata for album "{}" by "{}" found in a lookup table.'.format(album_name, artist_name))
        if track_name is not None:
            # Unfortunately, we basically can't use lookup table here, because we don't have album name
            # TODO: Think of a solution to this problem
            print('LastFmApi: Can\'t use album lookup table because album name wasn\'t provided.')
            track_metadata = self.track_metadata_lookup.get(artist_name + '/' + track_name)
            if track_metadata is None:  # If there is no metadata stored then download it
                if album_metadata is None:  # Check whether album metadata is already present
                    update_album_metadata = True
                    if DEBUG_MODE:
                        print('LastFmApi: Updating album metadata by the way.')
                else:
                    update_album_metadata = False
                if DEBUG_MODE:
                    print('LastFmApi: Downloading metadata for song "{}" by "{}".'.format(track_name, artist_name))
                album_metadata, track_metadata = \
                    self._get_metadata_using_track_name(artist_name, track_name, update_album_metadata)
        if track_metadata == {}:  # If track metadata is empty, change it to None
            track_metadata = None
        return album_metadata, track_metadata

    def _get_metadata_using_album_name(self, artist_name, album_name, enable_autocorrect=0):
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
        album_metadata = {}
        if album.get('image') is not None:
            album_metadata['cover_url'] = album.get('image')[-1].get('#text'),
        if album.get('wiki') is not None:
            album_metadata['wiki'] = album.get('wiki').get('content')
            album_metadata['wiki_summary'] = album.get('wiki').get('summary')
        if album.get('tags') is not None:
            album_metadata['tags'] = album.get('tags').get('tag')
        if album.get('tracks') is not None:
            tracklist = album.get('tracks').get('track')
            tracklist_titles = [track.get('name') for track in tracklist]  # Get only names of the songs
            album_metadata['tracklist'] = tracklist_titles
        if album.get('wiki') is not None:
            album_metadata['wiki'] = album.get('wiki').get('content')
            album_metadata['wiki_summary'] = album.get('wiki').get('summary')
        self.album_metadata_lookup[artist_name + '/' + album_name] = album_metadata
        return album_metadata

    def _get_metadata_using_track_name(self, artist_name, track_name, update_album_metadata, enable_autocorrect=0):
        """

        :param artist_name:
        :param track_name:
        :param update_album_metadata: Whether update album metadata or not.
        :param enable_autocorrect:
        :return:
        """
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
        # Handle errors
        if decoded_response.get('error') is not None:
            raise LastFmApiException("""An error occurred while trying to receive data from lastFm API.
                    Error number: {}, 
                    Error message: {}""".format(decoded_response.get('error'), decoded_response.get('message')))
        track_metadata = {}
        album_metadata = {}
        track = decoded_response.get('track')
        if track.get('toptags') is not None:
            album_metadata['tags'] = track.get('toptags').get('tag')
        if track.get('wiki') is not None:
            track_metadata['wiki'] = track.get('wiki').get('content')
            track_metadata['wiki_summary'] = track.get('wiki').get('summary')
        self.track_metadata_lookup[artist_name + '/' + track_name] = track_metadata
        album = track.get('album')
        if album is not None:
            if album.get('image') is not None:
                album_metadata['cover_url'] = album.get('image')[-1].get('#text')
            if update_album_metadata:
                album_name = album.get('title')
                self.album_metadata_lookup[artist_name + '/' + album_name] = album_metadata
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
