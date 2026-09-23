"""Colour readings from the sensor on extension port EXT1 of the FloorPro.

Run: scirodev run ble demo.py   (FloorPro on Port.A, colour sensor on EXT1)

Prints the raw red / green / blue / clear readings, the colour as hue /
saturation / value and the nearest named colour. RIGHT button cycles the
illumination LED through 25 / 100 / 0 %.
"""

from pybricks.tools import multitask, run_task, wait

from sciro.hubs import PeakHub
from sciro.parameters import Button, ExtPort, Port
from sciro.pump import ColorSensor

hub = PeakHub()
# The sensor is addressed by hub port and extension port; it does not matter
# which PUMP device carries the extension port.
color_sensor: ColorSensor = ColorSensor(Port.A, ExtPort.EXT1)


async def print_loop():
    while True:
        r, g, b, c, status = await color_sensor.read()
        hsv = await color_sensor.hsv()
        nearest = await color_sensor.color()
        print("RGBC: %5d %5d %5d %5d status=0x%02x | h %3d s %3d v %3d | %s" % (r, g, b, c, status, hsv.h, hsv.s, hsv.v, nearest))
        await wait(250)


async def led_loop():
    levels = [25, 100, 0]
    await color_sensor.set_light(levels[0])
    await color_sensor.set_gain(4)
    await color_sensor.set_integration(0xFD)
    print("Settings (led %, gain, atime):", color_sensor.settings())
    i = 0
    while True:
        while Button.RIGHT not in hub.buttons.pressed():
            await wait(10)
        while Button.RIGHT in hub.buttons.pressed():
            await wait(10)
        i = (i + 1) % len(levels)
        await color_sensor.set_light(levels[i])
        print("LED:", levels[i], "% -> settings", color_sensor.settings())


async def main():
    await multitask(print_loop(), led_loop())


run_task(main())
