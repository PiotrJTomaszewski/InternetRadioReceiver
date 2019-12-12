import urllib.request
from io import BytesIO
import json
import pprint as pprint
import string


class AlbumNotFoundError(Exception):
    pass


class CoverNotFoundError(Exception):
    pass


class LastfmApi:
    # Get album cover URL using last.fm api
    def __init__(self, api_key_filename='lastfm.key'):
        # Read api key from file
        # TODO: Error handling needed
        with open(api_key_filename, 'r') as api_key_file:
            self._api_key = api_key_file.readline()
        if self._api_key[-1] == '\n':
            self._api_key = self._api_key[:-1]

    def get_cover_url(self, artist, album=None, song_title=None):
        # TODO: Error handling! Lastfm will return error code
        # TODO: What if no song is being played
        # TODO: What if song is missing parameters
        if album is None:
            try:
                album = self.find_album_name(artist, song_title)
                album = self._encode(album)
            except AlbumNotFoundError:
                raise CoverNotFoundError
        artist = self._encode(artist)
        response = urllib.request.urlopen(
            'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={}&artist={}&album={}&autocorrect=1&format=json'.format(
                self._api_key, artist, album)).read()
        decoded_response = json.loads(response)
        try:
            cover_url = decoded_response['album']['image'][-1]['#text']
        except KeyError:
            message = decoded_response.get('message')
            if message is not None:
                print('Error: ' + message)
            else:
                print('Error while finding album')
            raise CoverNotFoundError
        return cover_url

    def find_album_name(self, artist, song_title):
        artist = self._encode(artist)
        song_title = self._encode(song_title)
        print(artist, song_title)
        response = urllib.request.urlopen(
            'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={}&artist={}&track={}&autocorrect=1&format=json'.format(
                self._api_key, artist, song_title)).read()
        decoded_response = json.loads(response)
        try:
            album = decoded_response['track']['album']['title']
        except KeyError:
            message = decoded_response.get('message')
            if message is not None:
                print('Error: ' + message)
            else:
                print('Error while finding album')
            raise AlbumNotFoundError
        return album

    def _encode(self, input_string):
        # TODO: Do it in one pass
        encoded_string = input_string
        encoded_string = encoded_string.replace(' ', '+')
        encoded_string = encoded_string.replace('&', '%26')
        slash_pos = encoded_string.find('/')
        if slash_pos != -1:
            encoded_string = encoded_string[:slash_pos]
        # encoded_string = ascii(encoded_string)  # Figure out how to do this properly
        # TODO: Characters not working: '
        return encoded_string


if __name__ == "__main__":
    lastfm = LastfmApi()
    import pprint

    pprint.pprint(lastfm.find_album_name('Metallica', 'Creeping death'))
