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
        self.name = "Rainbow scroll"
        self.rainbow_offset = 0
        self.rainbow_speed = 0.01
        self.rainbow_width = self.drawer.led_count

    def update(self):
        self.drawer.fill((0, 0, 0))

        for i in range(self.drawer.led_count):
            self.drawer.set_pixel_color(i, color_wheel(i / self.rainbow_width + self.rainbow_offset))
        self.rainbow_offset += self.rainbow_speed


class BounceMode(Mode):
    def __init__(self, manager):
        super(BounceMode, self).__init__(manager)
        self.name = "Bounce dot"
        self.color_pos = 0
        self.color_speed = 0
        self.pos = 0
        self.speed = 3
        self.width = 5
        self.fade = 3
        self.glow_time = 6
        self.current_glow = 0

    def update(self):
        if self.current_glow > 0:
            self.current_glow -= 1
        length = self.drawer.led_count
        self.drawer.fill((0, 0, 0))

        self.pos += self.speed
        if self.pos < 0:
            self.pos = 0
            self.speed = -self.speed
            self.current_glow = self.glow_time
        if self.pos + self.width > length:
            self.pos = length - self.width
            self.speed = -self.speed
            self.current_glow = self.glow_time
        alpha = self.current_glow / self.glow_time

        self.color_pos += self.color_speed
        base_color = color_wheel(self.color_pos)

        dot_color = tuple(channel * (1 - alpha) + alpha for channel in base_color)
        for i in range(self.pos - self.fade, self.pos + self.width + self.fade):
            if i < 0 or i >= length:
                continue
            if i < self.fade:
                fadeval = i / self.fade
                color = tuple(channel * fadeval for channel in dot_color)
            elif i > self.pos + self.width:
                fadeval = self.pos + self.width + self.fade - i - 1
                color = tuple(channel * fadeval for channel in dot_color)
            else:
                color = tuple(dot_color)
            self.drawer.set_pixel_color(i, color)

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
