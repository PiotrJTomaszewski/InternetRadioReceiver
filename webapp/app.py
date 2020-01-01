from flask import Flask, render_template, redirect, request
from multiprocessing.managers import SyncManager
from mpd_control_client import MPDControlClient

app = Flask(__name__)

manager = SyncManager(address=('', 50000), authkey=b'abc')
shared_song_metadata = {}
shared_mpd_status = {}

mpd_client = MPDControlClient('localhost', 6600)


@app.before_first_request
def init():
    # Setup shared metadata access
    global shared_song_metadata, shared_mpd_status
    SyncManager.register('SharedSongMetadata')
    SyncManager.register('SharedMpdStatus')
    manager.connect()
    shared_song_metadata = manager.SharedSongMetadata()
    shared_mpd_status = manager.SharedMpdStatus()
    mpd_client.connect()


@app.route('/')
def main():
    playlist = mpd_client.get_playlist()
    return render_template('index.html', metadata=shared_song_metadata, stations=playlist, mpd_status=shared_mpd_status)


@app.route('/pause')
def pause():
    print('Pause')
    mpd_client.pause()
    return redirect('/')


@app.route('/play')
def play():
    print('Play')
    mpd_client.play()
    return redirect('/')


@app.route('/prev')
def prev_station():
    print('Prev')
    mpd_client.prev()
    return redirect('/')


@app.route('/next')
def next_station():
    print('Next')
    mpd_client.next()
    return redirect('/')


@app.route('/volume_up')
def volume_up():
    print("Vol up")
    mpd_client.increase_volume(5)
    return redirect('/')


@app.route('/volume_down')
def volume_down():
    print("Vol down")
    mpd_client.decrease_volume(5)
    return redirect('/')


@app.route('/switchTo/<station_id>')
def switch_to_station(station_id):
    print('Switch to ', station_id)
    mpd_client.play
    return redirect('/')


@app.route('/delete/<station_id>')
def delete_station(station_id):
    print('Delete ', station_id)
    # mpd_do_action(mpd_client.deleteid, id)
    return redirect('/')


@app.route('/add_station', methods=['GET'])
def add_station():
    station_address = request.args.get('new_station_address')
    print(station_address)
    return redirect('/')


# TODO: Idle for song change and then force refresh
# TODO: Save playlist
# TODO: Add stations


if __name__ == '__main__':
    app.run()
