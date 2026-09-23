# ColorSensor on the PeakHub (PUMP)

Demos for the colour sensor on an extension port of a PUMP device (today: the
FloorPro) connected to a PeakHub. The `sciro.pump.ColorSensor` class is built
into the PeakHub firmware; no driver file is needed next to the scripts.

## Setup

```
pip install scirodev            # the scirodev command + the sciro API stubs
scirodev run ble demo.py        # runs a script on the hub over Bluetooth
```

## Files

- `demo.py` — Raw RGBC, HSV and the nearest colour; RIGHT cycles the LED
- `calibration_demo.py` — Range calibration on the sensor: RIGHT starts / stops
  (sweep over the darkest and brightest surfaces meanwhile), LEFT clears
- `qc.py` — Prints the stored calibration table and whether it applies

## API in one look

```python
from pybricks.parameters import Color
from sciro.parameters import ExtPort, Port
from sciro.pump import ColorSensor

color = ColorSensor(Port.A, ExtPort.EXT1)   # or FloorPro(Port.A).color_sensor(1)
r, g, b, c, status = color.read()           # raw 16-bit counts at device resolution
hsv = color.hsv()                           # Color(h 0..359, s 0..100, v 0..100)
nearest = color.color()                     # e.g. Color.RED
color.detectable_colors((Color.RED, Color.BLUE, Color.NONE))
color.set_light(25)                         # illumination LED, percent
color.set_gain(4)                           # 1, 4, 16 or 64
color.set_integration(0xFD)                 # TCS3400 ATIME: (256 - atime) * 2.78 ms
print(color.settings())                     # (led %, gain, atime) in effect

color.calibrate(True)                       # sweep dark .. bright, then:
color.calibrate(False)                      # stored on the sensor, bound to the settings
print(color.calibration_status())           # "none" | "weak" | "ok" | "calibrating"
r8, g8, b8 = color.calibrated()             # what the sensor's own display shows
mins, maxs, profile, valid, ok, mask = color.calibration()
color.clear_calibration()
```

`hsv()` and `color()` use the calibrated colour whenever a valid calibration
applies to the current settings, so a calibrated white really is
`Color.WHITE`. Changing the LED, gain or integration time makes the stored
calibration "weak" (not applied) until you calibrate again under those settings.

Every reading method, `calibration_status()` included, also works with `await`
under `run_task` / `multitask`; `settings()` and `state()` are plain values.
A reading taken after a settings change waits for the first sample measured
with the new settings.
