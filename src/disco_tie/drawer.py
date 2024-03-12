from rpi_ws281x import *

MAX_CURRENT = 800
SUBPIXEL_CURRENT = 15
class LightStrip:
    def __init__(self,
                 led_count=70,
                 led_pin=18,
                 led_frequency=800_000,
                 overall_brightness = 0.1,
                 ):
        self.led_count = led_count
        self.overall_brightness = overall_brightness
        self.layers = [Layer(led_count)]
        # self.pixels = [(0,0,0) for i in range(led_count)]
        self.strip = Adafruit_NeoPixel(led_count, led_pin, led_frequency, 10, False,  255)
        self.strip.begin()

    def add_layer(self, alpha=0.0):
        self.layers.append(Layer(self.led_count, alpha=alpha))

    def draw(self):
        #ensure we don't exceed the max current
        result_layer = self.layers[0]
        for layer in self.layers[1:]:
            result_layer = result_layer + layer
        total_brightness = result_layer.sum_brightness() * self.overall_brightness
        total_current = SUBPIXEL_CURRENT * total_brightness
        if total_current < MAX_CURRENT:
            brightness_mult = 1.0
        else:
            brightness_mult = MAX_CURRENT / total_current

        #set all pixels
        for i, pixel in enumerate(result_layer):
            final_pixel = tuple(int(subpixel * brightness_mult * self.overall_brightness * 255) for subpixel in pixel[:3])
            self.strip.setPixelColor(i, Color(final_pixel[0], final_pixel[1], final_pixel[2]))

        self.strip.show()

    def set_pixel_color(self, pixel_id, color, layer=0):
        self.layers[layer].set_pixel_color(pixel_id, color)

    def fill(self, color, layer=0):
        self.layers[layer].fill(color)

    def clear(self):
        for layer in self.layers:
            layer.clear()
        self.draw()


class Layer:
    def __init__(self, num_pixels, alpha = 1.0):
        self.pixels = [(0.0, 0.0, 0.0, alpha) for i in range(num_pixels)]

    def set_pixel_color(self, pixel_id, color):
        if len(color) < 4:
            alpha = self.pixels[pixel_id][3]
            color = (color[0], color[1], color[2], alpha)

        for channel in color:
            if channel < 0 or channel > 1.0:
                raise ValueError(f"Values out of range for color {color}. all channels should be floats between 0.0 and 1.0")

        self.pixels[pixel_id] = color

    def fill(self, color):
        for i, _ in enumerate(self.pixels):
            self.set_pixel_color(i, color)

    def clear(self):
        self.fill(0.0, 0.0, 0.0)

    def set_pixel_alpha(self, pixel_id, alpha):
        color = self.pixels[pixel_id][:3] + (alpha,)

    def __add__(self, other):
        if not isinstance(other, Layer):
            raise TypeError(f"Can only add Layers to other Layers, (not {type(other)})")
        if len(self.pixels) != len(other.pixels):
            raise KeyError(f"Both Layers should have the same size, ({len(self.pixels)} vs {len(other.pixels)})")
        result = Layer(len(self.pixels))
        for i, color in enumerate(self.pixels):
            other_color = other.pixels[i]
            this_component = tuple(ch * (1 - other_color[3]) for ch in color[:3])
            other_component = tuple(ch * other_color[3] for ch in other_color[:3])
            result.pixels[i] = tuple(ch + other_component[j] for j, ch in enumerate(this_component)) + (color[3],)
        return result

    def __getitem__(self, index):
        return self.pixels[index]

    def sum_brightness(self):
        return sum([sum(color[:3]) for color in self.pixels])
