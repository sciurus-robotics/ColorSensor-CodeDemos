"""Colour readings from the sensor on the FloorPro's extension port EXT1.

Run: pybricksdev run ble demo.py   (FloorPro on Port.A, colour sensor on EXT1)

Prints red / green / blue, the colour as hue / saturation / value and the
nearest named colour; RIGHT button cycles the illumination LED through
25 / 100 / 0 %.
"""

from pybricks.hubs import InventorHub
from pybricks.parameters import Button, Port
from pybricks.tools import multitask, run_task, wait

from color_sensor import ColorSensor

hub = InventorHub()
color_sensor = ColorSensor(Port.A, ColorSensor.EXT1)


async def print_loop():
    while True:
        r, g, b = await color_sensor.rgb()
        hsv = await color_sensor.hsv()
        nearest = await color_sensor.color()
        print("RGB: %3d %3d %3d | h %3d s %3d v %3d | %s" % (r, g, b, hsv.h, hsv.s, hsv.v, nearest))
        await wait(250)


async def led_loop():
    levels = [25, 100, 0]
    i = 0
    await color_sensor.set_light(levels[i])
    print("LED:", levels[i], "%")
    while True:
        while Button.RIGHT not in hub.buttons.pressed():
            await wait(10)
        while Button.RIGHT in hub.buttons.pressed():
            await wait(10)
        i = (i + 1) % len(levels)
        await color_sensor.set_light(levels[i])
        print("LED:", levels[i], "%")


run_task(multitask(print_loop(), led_loop()))
