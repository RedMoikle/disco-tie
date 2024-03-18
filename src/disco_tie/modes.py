class Mode:
    def __init__(self, manager):
        self.name = "Base mode"
        self.manager = manager
        self.drawer = manager.drawer

    def update(self):
        pass


class RainbowMode(Mode):
    def __init__(self, manager):
        super(RainbowMode, self).__init__(manager)
        self.name="Rainbow scroll"
        self.rainbow_offset = 0
        self.rainbow_speed = 1
        self.rainbow_width = 70

    def update(self):
        # test anim
        self.drawer.fill((0, 0, 0))
        # self.drawer.pixels[self.current_pixel] = (1.0, 0, 0)

        # if self.current_pixel == 0 and self.speed < 0:
        #    self.speed *= -1
        # elif self.current_pixel == self.led_count - 1 and self.speed > 0:
        #    self.speed *= -1
        # self.current_pixel += self.speed

        for i in range(self.drawer.led_count):
            self.drawer.set_pixel_color(i, color_wheel(i / self.rainbow_width + self.rainbow_offset))
        self.rainbow_offset += self.rainbow_speed


def color_wheel(pos):
    pos = pos % 1.0
    if pos < 1 / 3:
        return (pos * 3, 1.0 - pos * 3, 0)
    elif pos < 2 / 3:
        pos -= 1 / 3
        return (1.0 - pos * 3, 0, pos * 3)
    else:
        pos -= 2 / 3
        return (0, pos * 3, 1.0 - pos * 3)
