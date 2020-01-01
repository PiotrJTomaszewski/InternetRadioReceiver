from multiprocessing.managers import SyncManager
import time

from oled_display import OledDisplay
from mpd_control_client import MPDControlClient
from buttons import ButtonReader
from tft_display import TftDisplay


def system_poweroff():
    pass


class Control:
    def __init__(self):
        # Sync manager
        self.manager = SyncManager(address=('', 50000), authkey=b'abc')
        self.manager.register('SharedSongMetadata')
        self.manager.register('SharedMpdStatus')
        self.manager.register('ControlPanelNewSongEvent')
        self.manager.register('ControlPanelNewPlayerMetadataEvent')
        self.manager.connect()
        self.shared_song_metadata = self.manager.SharedSongMetadata()
        self.shared_mpd_stauts = self.manager.SharedMpdStatus()
        self.new_song_event = self.manager.ControlPanelNewSongEvent()
        self.new_player_metadata_event = self.manager.ControlPanelNewPlayerMetadataEvent()

        # Buttons
        self.mpd_client = MPDControlClient('localhost', 6600)
        callbacks = {
            'button1': self.mpd_client.play,
            'button2': self.mpd_client.pause,
            'button3': self.mpd_client.prev_station,
            'button4': self.mpd_client.next_station,
            'encoder_left': self.mpd_client.decrease_volume,
            'encoder_right': self.mpd_client.increase_volume,
            'encoder_button': system_poweroff
        }
        self.buttons = ButtonReader(callbacks)
        self.buttons.start_reading_thread()

        # TFT display
        self.tft_display = TftDisplay(new_song_event=self.new_song_event,
                                      metadata_source=self.tft_metadata_source)
        self.tft_display.start_display_thread()

        # OLED display
        self.oled_display = OledDisplay(new_metadata_event=self.new_player_metadata_event,
                                        metadata_source=self.oled_metadata_source)
        self.oled_display.start_display_thread()

    def oled_metadata_source(self):
        track_metadata = self.shared_song_metadata
        player_metadata = self.shared_mpd_stauts
        return track_metadata, player_metadata

    def new_song_wait_thread_function(self):
        self.new_song_event.wait()
        self.new_song_event.clear()

    def tft_metadata_source(self):
        return self.shared_song_metadata


if __name__ == "__main__":
    control = Control()
