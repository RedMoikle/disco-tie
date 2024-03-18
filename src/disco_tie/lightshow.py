from signal import pause

from gpiozero import LED, Button
from disco_tie import strandtest
from disco_tie.manager import Manager
from disco_tie.drawer import LightStrip
from disco_tie.options import Option

BLINKER = LED(21)
OPTIONS_BTN = Button(22)
MINUS_BTN = Button(27)
PLUS_BTN = Button(17)
POWER_BTN = Button(3, hold_time=5)


def clear_leds():
    BLINKER.off()


def shutdown():
    clear_leds()
    os.system("sudo poweroff")


def minus_pressed():
    print("-")


def plus_pressed():
    print("+")


def options_pressed():
    print("Opt")


if __name__ == "__main__":
    if OPTIONS_BTN.is_pressed and POWER_BTN.is_pressed:
        print("safe mode")
    else:
        manager = Manager(led_count=72,
                          blinker=BLINKER,
                          options_btn=OPTIONS_BTN,
                          plus_btn=PLUS_BTN,
                          minus_btn=MINUS_BTN,
                          power_btn=POWER_BTN,)
        manager.run()
        #strandtest.start_show(clear=True)
        #pause()
