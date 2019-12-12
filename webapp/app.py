from flask import Flask, render_template, redirect, request
from mpd import MPDClient, base
from metadata import get_metadata
from lastfmApi import LastfmApi, CoverNotFoundError

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
def main():
    global mpd_client, lastfm
    mpd_status = mpd_do_action(mpd_client.status)
    metadata = get_metadata(mpd_client)
    playlist = mpd_get_playlist()
    # try:
    #     metadata = get_metadata(mpd_client)
    # except ValueError:
    #     print('Nothing is being played')
    #     return render_template('index.html', metadata={}, album_cover='', mpd_status=mpd_status)  # TODO: Display message if nothing is playing
    # TODO: Check if the song is different than before to avoid asking again for the same cover
    album_cover = ''
    if metadata['artist'] != 'Unknown':
        try:
            album_cover = lastfm.get_cover_url(artist=metadata['artist'], song_title=metadata['title'])
            print(album_cover)
        except CoverNotFoundError:
            pass
    return render_template('index.html', metadata=metadata, album_cover=album_cover, mpd_status=mpd_status,
                           stations=playlist)


@app.route('/pause')
def pause():
    print('Pause')
    mpd_do_action(mpd_client.pause, 1)
    return redirect('/')


@app.route('/play')
def play():
    print('Play')
    mpd_do_action(mpd_client.pause, 0)
    return redirect('/')


@app.route('/prev')
def prev_station():
    print('Prev')
    mpd_do_action(mpd_client.previous)
    return redirect('/')


@app.route('/next')
def next_station():
    print('Next')
    mpd_do_action(mpd_client.next)
    return redirect('/')


@app.route('/switchTo', methods=['GET'])
def switch_to_station():
    id = request.args.get('id')
    print('Switch to ', id)
    mpd_do_action(mpd_client.playid, id)
    return redirect('/')


@app.route('/delete', methods=['GET'])
def delete_station():
    id = request.args.get('id')
    print('Delete ', id)
    mpd_do_action(mpd_client.deleteid, id)
    return redirect('/')


def mpd_do_action(action, parameter=None):
    action_done = False
    returned_value = None
    while not action_done:
        try:
            if parameter is not None:
                returned_value = action(parameter)
            else:
                returned_value = action()
            action_done = True
        except base.ConnectionError:
            mpd_client.connect('localhost', 6600)
            pass
    return returned_value


def mpd_get_playlist():
    playlist = mpd_do_action(mpd_client.playlistid)
    return playlist


# TODO: Idle for song change and then force refresh
# TODO: Save playlist
# TODO: Add stations


if __name__ == '__main__':
    app.run()
