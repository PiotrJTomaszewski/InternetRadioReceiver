from multiprocessing.managers import SyncManager
from multiprocessing import Event

manager = SyncManager(address=('', 50000), authkey=b'abc')
manager.register('ControlPanelNewSongEvent')
manager.connect()

new_song_event = manager.ControlPanelNewSongEvent()

new_song_event.wait()
print(new_song_event.is_set())
new_song_event.unset()
new_song_event.wait()
