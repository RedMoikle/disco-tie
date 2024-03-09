from signal import pause
from gpiozero import LED, Button
import strandtest
from manager import Manager

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
    drawer = None
    manager = Manager(blinker=BLINKER,
                      options_btn=OPTIONS_BTN,
                      plus_btn=PLUS_BTN,
                      minus_btn=MINUS_BTN,
                      power_btn=POWER_BTN,
                      drawer=drawer)
    strandtest.start_show(clear=True)
    pause()
