import time
import os

from disco_tie.drawer import LightStrip
from disco_tie.options import Option
from disco_tie.modes import *

STARTUP_TIME = time.time()

MODE_COLORS = {0: (1, 1, 1),
               1: (0.5, 0.5, 1)}


class Manager:
    def __init__(self, led_count=74, blinker=None, options_btn=None, minus_btn=None, plus_btn=None, power_btn=None,
                 run=False):
        self.running = run
        self.framerate = 30
        self.options_hold_time = 3
        self.min_brightness = 0.01
        self.led_count = led_count
        self.speed = 1
        self.current_pixel = 0
        self.brightness_steps = 20
        self.blinker = blinker
        self.options_btn = options_btn
        self.minus_btn = minus_btn
        self.plus_btn = plus_btn
        self.power_btn = power_btn
        self.drawer = LightStrip(led_count=led_count,
                                 led_pin=18,
                                 led_frequency=800_000,
                                 overall_brightness=1.0, )

        self.opt_held = False
        self.opt_pressed = False
        self.opt_released = False
        self.plus_held = False
        self.plus_pressed = False
        self.plus_released = False
        self.minus_held = False
        self.minus_pressed = False
        self.minus_released = False
        self.power_held = False
        self.audio_sample = None

        self.deltatime = 1 / self.framerate
        self.blinker.blink()
        self.power_btn.when_held = self.shutdown

        self.options_active = False
        self.options_activated = False
        self.options_setting = 0
        self.options_last_press_time = None
        self.options_activated_time = None

        self.main_strip = self.drawer.layers[0]
        self.knot = self.drawer.add_layer()
        self.options_layer = self.drawer.add_layer()
        for i in range(6):
            self.knot.set_pixel_alpha(i, 1.0)
        self.set_knot_color((1.0, 1.0, 1.0))

        self.options = []
        self.modes = [RainbowMode(self),
                      BounceMode(self)]
        self.selected_mode = 0

        self.add_option("brightness",
                        color=(1.0, 1.0, 1.0),
                        increase_func=self._set_brightness,
                        decrease_func=self._set_brightness,
                        init_func=self._set_brightness,
                        maximum=self.brightness_steps,
                        wrap=False)
        self.add_option("mode",
                        color=(1.0, 1.0, 0.0),
                        increase_func=self._set_mode,
                        decrease_func=self._set_mode,
                        init_func=self._set_mode,
                        maximum=1,
                        wrap=True)

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
        prev_opt = self.opt_held
        self.opt_held = self.options_btn.is_pressed
        if self.opt_held and not prev_opt:
            self.opt_pressed = True
        else:
            self.opt_pressed = False
        if not self.opt_held and prev_opt:
            self.opt_released = True
        else:
            self.opt_released = False

        self.power_held = self.power_btn.is_pressed

        prev_plus = self.plus_held
        self.plus_held = self.plus_btn.is_pressed
        if self.plus_held and not prev_plus:
            self.plus_pressed = True
        else:
            self.plus_pressed = False
        if not self.plus_held and prev_plus:
            self.plus_released = True
        else:
            self.plus_released = False

        prev_minus = self.minus_held
        self.minus_held = self.minus_btn.is_pressed
        if self.minus_held and not prev_minus:
            self.minus_pressed = True
        else:
            self.minus_pressed = False
        if not self.minus_held and prev_minus:
            self.minus_released = True
        else:
            self.minus_released = False

    def _get_audio(self):
        self.audio_sample = [0]

    def _draw(self):
        if self.drawer is not None:
            self.drawer.draw()
            return
        self.print("drawing")

    def open_options(self):
        print("opening options")
        self.options_active = True
        self.options_layer.fill_alpha(1.0, end=6)

    def close_options(self):
        print("closing options")
        self.options_active = False
        self.options_layer.fill_alpha(0.0)

    def next_setting(self):
        print("next option")
        self.options_setting += 1
        if self.options_setting >= len(self.options):
            self.options_setting = 0

    def increase_setting(self):
        print("Increase")
        self.options[self.options_setting].increase()

    def decrease_setting(self):
        print("Decrease")
        self.options[self.options_setting].decrease()

    def _set_brightness(self, integer):
        self.drawer.overall_brightness = integer / self.brightness_steps
        if self.drawer.overall_brightness < self.min_brightness:
            self.drawer.overall_brightness = self.min_brightness

    def _set_mode(self, mode_num):
        self.selected_mode = mode_num
        self.set_knot_color(MODE_COLORS.get(mode_num, (1, 1, 1)))
        print(f"Switching to {self.modes[self.mode].name} mode")

    def update(self):
        if int(time.time()) % 2:
            opt_color = self.options[self.options_setting].color
            self.options_layer.fill(opt_color, end=4)
        else:
            self.options_layer.fill((0.0, 0.0, 0.0), end=6)

        if self.opt_pressed:
            self.options_last_press_time = time.time()
            if self.options_active:
                self.next_setting()

        if self.opt_released:
            self.options_activated = False

        if self.opt_held and not self.options_activated and time.time() > self.options_last_press_time + self.options_hold_time:
            self.options_activated = True
            if not self.options_active:
                self.open_options()
            else:
                self.close_options()

        if self.options_active:
            if self.plus_pressed:
                self.increase_setting()
            if self.minus_pressed:
                self.decrease_setting()

        mode = self.modes[self.selected_mode]
        mode.update()

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
        self.running = False
        if time.time() > STARTUP_TIME + 10:
            print("Restarting in 5 seconds")
            time.sleep(5)
            os.system("sudo poweroff")

    def add_option(self, option_name, color, increase_func, decrease_func, init_func, maximum=10, wrap=False):
        option = Option(option_name, color, increase_func, decrease_func, init_func, maximum, wrap)
        self.options.append(option)

    def set_knot_color(self, color):
        for i in range(4):
            self.knot.set_pixel_color(i, color)
