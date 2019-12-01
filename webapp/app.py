from flask import Flask, render_template
from mpd import MPDClient
from metadata import get_metadata
from lastfmApi import LastfmApi

app = Flask(__name__)
mpd_client = None
lastfm = None


@app.before_first_request
def connect_to_mpd_client():
    global mpd_client, lastfm
    mpd_client = MPDClient()
    mpd_client.connect('localhost', 6600)
    lastfm = LastfmApi()
    print(mpd_client.mpd_version)


@app.route('/')
def hello_world():
    global mpd_client, lastfm
    metadata = get_metadata(mpd_client)
    # TODO: Check if the song is different than before to avoid asking again for the same cover
    if metadata['artist'] != 'Unknown':
        album_cover = lastfm.get_cover_url(artist=metadata['artist'], song_title=metadata['title'])
    else:
        album_cover = ''
    print(album_cover)
    return render_template('index.html', metadata=metadata, album_cover=album_cover)


if __name__ == '__main__':
    app.run()
