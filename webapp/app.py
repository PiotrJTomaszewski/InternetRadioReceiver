from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit
from multiprocessing.managers import SyncManager
from mpd_control_client import MPDControlClient

FLASK_DEBUG = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Very Secret Key! Please don\'t look!'
socketio = SocketIO(app)

manager = SyncManager(address=('', 50000), authkey=b'abc')
shared_song_metadata = {}
shared_mpd_status = {}
shared_playlist = {}
new_status_event = None

mpd_client = MPDControlClient('localhost', 6600)


@socketio.on('has_status_changed_request')
def has_status_changed():
    print('Client asking about status change')
    if new_status_event is not None:
        value_to_return = new_status_event.is_set()
        new_status_event.clear()
        emit('has_status_changed_reply', value_to_return, broadcast=True)


@app.before_first_request
def init():
    # Setup shared metadata access
    global shared_song_metadata, shared_mpd_status, new_status_event, shared_playlist
    SyncManager.register('SharedSongMetadata')
    SyncManager.register('SharedMpdStatus')
    SyncManager.register('SharedPlaylist')
    SyncManager.register('WebappNewStatusEvent')
    manager.connect()
    shared_song_metadata = manager.SharedSongMetadata()
    shared_mpd_status = manager.SharedMpdStatus()
    shared_playlist = manager.SharedPlaylist()
    new_status_event = manager.WebappNewStatusEvent()


@app.route('/')
def main():
    stations = mpd_client.get_stations()
    return render_template('index.html', metadata=shared_song_metadata, stations=stations, mpd_status=shared_mpd_status)


@socketio.on('pause')
def pause():
    print('Pause')
    mpd_client.pause()


@socketio.on('play')
def play():
    print('Play')
    mpd_client.play()


@socketio.on('prev_station')
def prev_station():
    print('Prev')
    mpd_client.prev_station()


@socketio.on('next_station')
def next_station():
    print('Next')
    mpd_client.next_station()


@socketio.on('volume_up')
def volume_up():
    print("Vol up")
    mpd_client.increase_volume(5)


@socketio.on('volume_down')
def volume_down():
    print("Vol down")
    mpd_client.decrease_volume(5)


@socketio.on('switch_to')
def switch_to_station(station_id):
    print('Switch to ', station_id)
    mpd_client.switch_to_station(station_id)


@socketio.on('delete_station')
def delete_station(station_id):
    mpd_client.delete_station(station_id)
    # mpd_client.save_stations()# TODO: Move that?


@socketio.on('add_station')
def add_station(address):
    mpd_client.add_station(address)
    # mpd_client.save_stations()# TODO: Move that?


# TODO: Save playlist


if __name__ == '__main__':
    # socketio.run(app, host="0.0.0.0", use_reloader=True)
    socketio.run(app, host="0.0.0.0")
