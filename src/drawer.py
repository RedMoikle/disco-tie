from rpi_ws281x import *

MAX_CURRENT = 2000
SUBPIXEL_CURRENT = 20
class LightStrip:
    def __init__(self,
                 led_count=70,
                 led_pin=18,
                 led_frequency=800_000,
                 overall_brightness = 0.1,
                 ):
        self.overall_brightness = overall_brightness
        self.pixels = [(0,0,0) for i in range(led_count)]
        self.strip = Adafruit_NeoPixel(led_count, led_pin, led_frequency, overall_brightness)
        self.strip.begin()

    def draw(self):
        #ensure we don't exceed the max current
        total_brightness = sum(value for pixel in self.pixels for value in pixel) * self.overall_brightness
        total_current = SUBPIXEL_CURRENT * total_brightness
        if total_current < MAX_CURRENT:
            brightness_mult = 1.0
        else:
            brightness_mult = MAX_CURRENT / total_current

        #set all pixels
        for i, pixel in enumerate(self.pixels):
            final_pixel = (subpixel * brightness_mult * self.overall_brightness for subpixel in pixel)
            self.strip.setPixelColor(i, final_pixel)

        self.strip.show()

    def fill(self, color):
        self.pixels = [color for _ in self.pixels]

    def clear(self):
        self.fill((0,0,0))
        self.draw()
