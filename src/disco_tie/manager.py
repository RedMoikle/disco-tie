import time
import os


class Manager:
    def __init__(self, blinker=None, options_btn=None, minus_btn=None, plus_btn=None, power_btn=None, drawer=None,
                 run=False):
        self.running = run
        self.framerate = 30

        self.led_count = 74
        self.speed = 1
        self.current_pixel = 0

        self.blinker = blinker
        self.options_btn = options_btn
        self.minus_btn = minus_btn
        self.plus_btn = plus_btn
        self.power_btn = power_btn
        self.drawer = drawer

        self.opt_held = False
        self.plus_held = False
        self.minus_held = False
        self.power_held = False
        self.audio_sample = None

        self.deltatime = 1 / self.framerate
        self.blinker.blink()
        self.power_btn.when_held = self.shutdown

        self.rainbow_offset = 0
        self.rainbow_speed = 2
        self.rainbow_width = self.led_count

        if self.running:
            self._main_loop()

    def _main_loop(self):
        frame_end = None
        while self.running:
            if frame_end is None:
                frame_start = time.time()
            else:
                frame_start = frame_end

            self._get_inputs()
            self._get_audio()
            self.update()
            self._draw()

            frame_end = time.time()
            self.deltatime = frame_end - frame_start
            excess = 1 / self.framerate - self.deltatime
            if excess > 0:
                time.sleep(excess)

    def _get_inputs(self):
        self.opt_held = self.options_btn.is_pressed
        self.power_held = self.power_btn.is_pressed
        self.plus_held = self.plus_btn.is_pressed
        self.minus_held = self.minus_btn.is_pressed

    def _get_audio(self):
        self.audio_sample = [0]

    def _draw(self):
        if self.drawer is not None:
            self.drawer.draw()
            return
        self.print("drawing")

    def update(self):
        # test anim
        self.drawer.fill((0, 0, 0))
        #self.drawer.pixels[self.current_pixel] = (255, 0, 0)

        #if self.current_pixel == 0 and self.speed < 0:
        #    self.speed *= -1
        #elif self.current_pixel == self.led_count - 1 and self.speed > 0:
        #    self.speed *= -1
        #self.current_pixel += self.speed

        for i in range(self.led_count):
            self.drawer.pixels[i] = color_wheel(self.rainbow_offset / self.rainbow_width)
        self.rainbow_offset += self.rainbow_speed

    def clear_leds(self):
        self.blinker.off()
        if self.drawer is not None:
            self.drawer.clear()
            return
        print("clearing")

    def run(self):
        self.running = True
        self._main_loop()

    def shutdown(self):
        self.clear_leds()
        # os.system("sudo poweroff")

def color_wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)
