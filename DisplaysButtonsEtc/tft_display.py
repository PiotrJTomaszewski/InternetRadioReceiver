import Adafruit_GPIO.SPI as SPI
import ST7789 as TFT  # https://github.com/solinnovay/Python_ST7789


class TftDisplay:
    #TODO: Add welcome image
    def __init__(self, rst_pin, blk_pin, dc_pin):
        # Initialize TFT display
        # rst_pin, blk_pin, dc_pin - As GPIO number (int)
        spi = SPI.SpiDev(0, 0, max_speed_hz=40000000)
        self.width  = 240
        self.height = 240
        self.display = TFT.ST7789(spi=spi, mode=0b11, rst=rst_pin, dc=dc_pin, led=blk_pin)
        self.display.begin()
        self.display.clear()
        print("TftDisplay: Display initialized")

    def display_image(self, image):
        self.display.display(image)
        print("TftDisplay: Cover displayed")
