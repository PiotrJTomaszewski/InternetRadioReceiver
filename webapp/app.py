from flask import Flask, render_template, redirect, request
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
from mpd import MPDClient, base

app = Flask(__name__)

manager = SyncManager(address=('', 50000), authkey=b'abc')
shared_song_metadata = {}
shared_mpd_status = {}


@app.before_first_request
def init():
    global shared_song_metadata, shared_mpd_status
    SyncManager.register('SharedSongMetadata')
    SyncManager.register('SharedMpdStatus')
    manager.connect()
    shared_song_metadata = manager.SharedSongMetadata()
    shared_mpd_status = manager.SharedMpdStatus()


# global mpd_client, lastfm
# mpd_client = MPDClient()
# mpd_client.connect('localhost', 6600)
# print(mpd_client.mpd_version)


@app.route('/')
def main():
    # mpd_status = mpd_do_action(mpd_client.status)
    # metadata = get_metadata(mpd_client)
    # playlist = mpd_get_playlist()

    playlist = {}
    #

    return render_template('index.html', metadata=shared_song_metadata, stations=playlist, mpd_status=shared_mpd_status)


@app.route('/pause')
def pause():
    print('Pause')
    # mpd_do_action(mpd_client.pause, 1)
    return redirect('/')


@app.route('/play')
def play():
    print('Play')
    # mpd_do_action(mpd_client.pause, 0)
    return redirect('/')


@app.route('/prev')
def prev_station():
    print('Prev')
    # mpd_do_action(mpd_client.previous)
    return redirect('/')


@app.route('/next')
def next_station():
    print('Next')
    # mpd_do_action(mpd_client.next)
    return redirect('/')


@app.route('/switchTo', methods=['GET'])
def switch_to_station():
    id = request.args.get('id')
    print('Switch to ', id)
    # mpd_do_action(mpd_client.playid, id)
    return redirect('/')


@app.route('/delete', methods=['GET'])
def delete_station():
    id = request.args.get('id')
    print('Delete ', id)
    # mpd_do_action(mpd_client.deleteid, id)
    return redirect('/')


# TODO: Idle for song change and then force refresh
# TODO: Save playlist
# TODO: Add stations


if __name__ == '__main__':
    app.run()
