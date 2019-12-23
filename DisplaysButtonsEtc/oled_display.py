import busio
from board import SCL, SDA
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont


class OledDisplay:
    # TODO: Add welcome message
    def __init__(self, metadata_object, interval=4):
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
