"""Calibrate the colour sensor on extension port EXT1 from the PeakHub.

Run: scirodev run ble calibration_demo.py   (FloorPro on Port.A, colour sensor on EXT1)

The calibration is a range sweep on the device, like the FloorPro's IR array:
while it runs, show the sensor the darkest and the brightest surfaces (or all
the elements, including "nothing") it will have to tell apart. Stopping stores
the table on the sensor, bound to the LED, gain and integration time in force;
changing those later marks the calibration "weak" until you calibrate again.
RIGHT starts and stops, LEFT clears the stored calibration.
"""

from pybricks.tools import multitask, run_task, wait

from sciro.hubs import PeakHub
from sciro.parameters import Button, ExtPort, Port
from sciro.pump import ColorSensor

hub = PeakHub()
color: ColorSensor = ColorSensor(Port.A, ExtPort.EXT1)


async def wait_for(button):
    while button not in hub.buttons.pressed():
        await wait(20)
    while hub.buttons.pressed():
        await wait(20)


async def print_loop():
    while True:
        raw = await color.read()
        r, g, b = await color.calibrated()
        hsv = await color.hsv()
        status = await color.calibration_status()
        print("raw %5d %5d %5d %5d | calibrated RGB %3d %3d %3d | h %3d s %3d v %3d | %s | %s"
              % (raw[0], raw[1], raw[2], raw[3], r, g, b, hsv.h, hsv.s, hsv.v, await color.color(), status))
        if status == "calibrating":
            # The table stream shows the running min / max while calibrating.
            mins, maxs, profile, valid, applicable, visited = await color.calibration()
            print("  range so far: " + "  ".join("%s %5d..%5d%s" % (n, lo, hi, "" if visited & (1 << i) else "?")
                                                  for i, (n, lo, hi) in enumerate(zip("RGBC", mins, maxs))))
        await wait(500)


async def control_loop():
    print("Settings (led %, gain, atime):", color.settings(), "calibration:", await color.calibration_status())
    print("RIGHT: start / stop calibration, LEFT: clear the stored calibration")
    while True:
        pressed = hub.buttons.pressed()
        if Button.RIGHT in pressed:
            await wait_for(Button.RIGHT)
            if await color.calibration_status() == "calibrating":
                await color.calibrate(False)
                mins, maxs, profile, valid, applicable, visited = await color.calibration()
                print("stored:", "valid" if valid else "INCOMPLETE (visited mask 0x%x)" % visited)
                print("  min R G B C:", mins)
                print("  max R G B C:", maxs)
                print("  profile (led %, gain, atime):", profile)
            else:
                await color.calibrate(True)
                print("Calibrating: sweep over the darkest and brightest surfaces, then press RIGHT.")
        elif Button.LEFT in pressed:
            await wait_for(Button.LEFT)
            await color.clear_calibration()
            print("Calibration cleared.")
        await wait(20)


async def main():
    await multitask(control_loop(), print_loop())


run_task(main())
