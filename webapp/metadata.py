from mpd import base
import re


def get_metadata(mpd_client):
    return get_metadata_shoutcast(mpd_client)


def get_metadata_shoutcast(mpd_client):
    metadata = {}
    metadata_recieved = False
    metadata_raw = None
    while not metadata_recieved:
        try:
            metadata_raw = mpd_client.currentsong()
            metadata_recieved = True
        except base.ConnectionError:
            mpd_reconnect(mpd_client)
            print('MPD connection error. Trying to reconnect')

    metadata['radio_address'] = metadata_raw['file']
    metadata['radio_name'] = metadata_raw['name']
    raw_title = metadata_raw['title']  # The title consists of song title, artist name and the release year
    raw_title = raw_title.rstrip()
    if re.match('\([0-9]{4}\)', raw_title[-6:]):  # There is a year at the end of the title
        metadata['year'] = raw_title[-6:]
        metadata['year'] = metadata['year'][1:-1]  # Remove parenthesis
        raw_title = raw_title[:-6]
    try:
        metadata['artist'], metadata['title'] = raw_title.split('-')
    except ValueError:
        metadata['title'] = raw_title
        metadata['artist'] = 'Unknown'
    # Remove unnecessary whitespaces
    metadata['title'] = metadata['title'].rstrip()
    metadata['title'] = metadata['title'].lstrip()
    metadata['artist'] = metadata['artist'].lstrip()
    metadata['artist'] = metadata['artist'].rstrip()
    return metadata


def mpd_reconnect(mpd_client):
    mpd_client.connect('localhost', 6600)
