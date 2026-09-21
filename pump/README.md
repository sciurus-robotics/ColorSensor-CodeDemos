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
```

Every reading method also works with `await` under `run_task` / `multitask`.
A reading taken after a settings change waits for the first sample measured
with the new settings.
