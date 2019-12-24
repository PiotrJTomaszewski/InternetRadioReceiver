from multiprocessing.managers import SyncManager
import multiprocessing
import threading
from oled_display import OledDisplay
import time


#
# manager = SyncManager(address=('', 50000), authkey=b'abc')
# manager.register('ControlPanelNewSongEvent')
# manager.connect()

# new_song_event = manager.ControlPanelNewSongEvent()

# new_song_event.wait()
# print(new_song_event.is_set())
# new_song_event.unset()
# new_song_event.wait()


def send_oled_metadata():
    metadata = {'track': {'name': 'Angus Mcfife'}, 'artist': 'Gloryhammer',
                'album': {'name': 'Tales from the Kingdom of Fife'},
                'radio': {'name': 'Hardcore radio', 'address': 'https://www.LoremIpsumDolores.est'}}
    player_metadata = {'state': 'playing'}
    return metadata, player_metadata

event = threading.Event()
oled = OledDisplay(event, send_oled_metadata)
time.sleep(10)
event.set()
