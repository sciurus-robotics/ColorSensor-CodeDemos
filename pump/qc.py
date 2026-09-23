"""Quality check of the colour sensor's stored calibration.

Run: scirodev run ble qc.py   (FloorPro on Port.A, colour sensor on EXT1)

Prints the stored calibration table (minimum and maximum raw count per channel,
the settings profile it was taken under, whether it is complete and applies to
the current settings) and the current raw and calibrated readings. Small spans
mean the calibration sweep did not cover dark and bright.
"""

from pybricks.tools import run_task

from sciro.parameters import ExtPort, Port
from sciro.pump import ColorSensor

color: ColorSensor = ColorSensor(Port.A, ExtPort.EXT1)


async def qc():
    print("Settings (led %, gain, atime):", color.settings(), "| calibration:", await color.calibration_status())
    mins, maxs, profile, valid, applicable, visited = await color.calibration()
    print("stored profile (led %, gain, atime):", profile, "| valid:", valid, "| applies now:", applicable)
    for name, lo, hi, bit in zip("RGBC", mins, maxs, range(4)):
        print("  %s: min %5d  max %5d  span %5d %s" % (name, lo, hi, hi - lo, "" if visited & (1 << bit) else "(not visited)"))
    raw = await color.read()
    print("raw R G B C:", raw[:4], "status 0x%02x" % raw[4])
    print("calibrated R G B:", await color.calibrated(), "| hsv:", await color.hsv(), "|", await color.color())


run_task(qc())
