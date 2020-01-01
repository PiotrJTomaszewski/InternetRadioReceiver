import busio
from board import SCL, SDA
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time
import threading


class OledDisplay:
    # TODO: Add welcome message
    def __init__(self, new_metadata_event, metadata_source, interval=4):
        # Define screen parameters and connect to it
        i2c = busio.I2C(SCL, SDA)
        self.width = 128
        self.height = 32
        pixel_depth = "1"  # Black & white display
        self.max_onscreen_chars = 20  # Max number of chars that fits on one screen
        self.interval = interval  # time in seconds for which each chunk will be visible on the screen
        self.display = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, i2c)
        # Clear the display
        self.display.fill(0)
        self.display.show()
        print("OledDisplay: Display initialized")
        # Create blank image for drawing
        self.image = Image.new(pixel_depth, (self.width, self.height))
        # Create drawing object to draw on image
        self.draw = ImageDraw.Draw(self.image)
        # Load a font
        self.font = ImageFont.truetype('LiberationMono-Regular.ttf', 10)
        print("OledDisplay: Font loaded")
        self.new_metadata_event = new_metadata_event
        self.metadata_source = metadata_source
        # Start display thread
        self.display_thread = threading.Thread(target=self._display_metadata_thread)

    def start_display_thread(self):
        self.display_thread.start()

    def _prepare_text(self):
        metadata, player_status = self.metadata_source()
        song_text = (metadata.get('track').get('name') or 'Unknown',
                     metadata.get('artist') or 'Unknown',
                     metadata.get('album').get('name') or 'Unknown')
        radio_text = (metadata.get('radio').get('name') or 'Unknown',
                      metadata.get('radio').get('address') or 'Unknown',
                      'Status: ' + (player_status.get('state') or 'Unknown'))
        return song_text, radio_text

    def _display_metadata_thread(self):
        # Continuously displays song metadata (title, artist, album), radio metadata (radio name, radio address)
        # and current MPD status on the oled display. If some piece of information is too long
        # to fit on one screen, it chops it into chunks and iterates over them at a given time interval
        print("OledDisplay: Display metadata thread started")
        song_text_splitted = [['Welcome to'], ['Internet Radio'], ['Receiver']]
        radio_text_splitted = [['No'], ['Radio'], ['Playing']]
        max_num_of_chunks_song = 1
        max_num_of_chunks_radio = 1
        counter = 0
        while True:
            # Check if metadata has changed
            if self.new_metadata_event.is_set():
                song_text, radio_text = self._prepare_text()
                self.new_metadata_event.clear()
                song_text_splitted = [self._split_into_chunks(x) for x in song_text]
                radio_text_splitted = [self._split_into_chunks(x) for x in radio_text]
                max_num_of_chunks_song = max([len(x) for x in song_text_splitted])
                max_num_of_chunks_radio = max([len(x) for x in radio_text_splitted])
            if counter < 3:  # Song to radio display ratio 3:1
                self.display_text(song_text_splitted, max_num_of_chunks_song)
            else:
                self.display_text(radio_text_splitted, max_num_of_chunks_radio)
            counter = (counter + 1) % 4

    def display_text(self, lines_splitted, max_number_of_chunks):
        for i in range(max_number_of_chunks):
            # Clear display
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            for line_num in range(len(lines_splitted)):  # For each line
                self.draw.text((1, 10 * line_num),
                               lines_splitted[line_num][i % len(lines_splitted[line_num])], font=self.font, fill=255)
            # Display
            self.display.image(self.image)
            self.display.show()
            time.sleep(self.interval)

    def _split_into_chunks(self, text):
        # Splits given string into chunks that could fit on the screen and returns it as a list.
        # Removes leading spaces from chunks
        return [text[i:i + self.max_onscreen_chars].lstrip() for i in range(0, len(text), self.max_onscreen_chars)]


if __name__ == '__main__':
    oled = OledDisplay()
    oled._display_metadata_thread()
