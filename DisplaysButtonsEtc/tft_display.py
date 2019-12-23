import Adafruit_GPIO.SPI as SPI
import ST7789 as TFT  # https://github.com/solinnovay/Python_ST7789
import urllib.request
from io import BytesIO
from PIL import Image
from collections import OrderedDict


class ImageLookup(OrderedDict):
    """
    A lookup table to store images.
    Implements the LRU algorithm to limit the number of stored data.
    Code from an official Python documentation.
    """

    def __init__(self, max_size, *args, **kwds):
        self.maxsize = max_size
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class TftDisplay:
    # TODO: Add welcome image
    def __init__(self, rst_pin, dc_pin, blk_pin):
        # Initialize TFT display
        # rst_pin, blk_pin, dc_pin - As GPIO number (int)
        spi = SPI.SpiDev(0, 0, max_speed_hz=40000000)
        self.width = 240
        self.height = 240
        self.display = TFT.ST7789(spi=spi, mode=0b11, rst=rst_pin, dc=dc_pin, led=blk_pin)
        self.display.begin()
        self.display.clear()
        self.image_lookup = ImageLookup(20)
        print("TftDisplay: Display initialized")

    def download_and_display_image(self, url):
        image = self.image_lookup.get(url)
        if image is not None:  # Image was found in the lookup table
            print('TFTDisplay: Image was found in the lookup table')
        else:
            image = self.download_image(url)
        # image = Image.Image.convert(image, Image.MODES.RGB)
        self.display_image(image)

    def display_image(self, image):
        # TODO: Blend pause symbol into image?
        self.display.display(image)
        print("TftDisplay: Image displayed")

    def download_image(self, url):
        fd = urllib.request.urlopen(url)
        image_file = BytesIO(fd.read())
        # Open the image
        image = Image.open(image_file)
        image.thumbnail((240, 240), Image.ANTIALIAS)
        self.image_lookup[url] = image
        print("TFTFisplay: Image downloaded")
        return image


if __name__ == '__main__':
    url = 'https://avatars3.githubusercontent.com/u/34516276?s=88&v=4'
    tft_display = TftDisplay(26, 6, 13)
    # tft_display.display_image(a)
    tft_display.download_and_display_image(url)
