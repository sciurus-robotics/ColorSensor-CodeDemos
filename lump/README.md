# ColorSensor on LEGO hubs (Pybricks, LUMP)

Driver and demo for the colour sensor plugged into an extension port of a
FloorPro that is connected to a LEGO Prime / Inventor hub running
[Pybricks](https://pybricks.com). The FloorPro speaks LEGO's UART sensor
protocol (LUMP) there and reports the colour inside its own sensor message,
which `color_sensor.py` decodes through `pybricks.iodevices.PUPDevice`.

## Files

- `color_sensor.py` — `ColorSensor(port, ext_port)` driver: `rgb()`, `hsv()`,
  `color()`, `detectable_colors()`, `light()`, `set_light()`, `saturated()`,
  `error()`. Self-contained; the FloorPro line-sensor driver is not needed (see
  [FloorPro-CodeDemos](https://github.com/sciurus-robotics/FloorPro-CodeDemos)
  for that).
- `demo.py` — Prints RGB, HSV and the nearest colour; RIGHT cycles the LED

Run with [`pybricksdev`](https://github.com/pybricks/pybricksdev), e.g.
`pybricksdev run ble demo.py` from this folder (the driver module must sit next
to the script).

## Notes

- Over LUMP the sensor delivers red, green and blue scaled to 8 bit at fixed
  gain and integration time, plus the LED level. Raw 16-bit readings and the
  gain / integration settings are available over PUMP only.
- `hsv()` returns a `pybricks.parameters.Color`; `color()` picks the nearest of
  the detectable colours with the same matcher as `pybricks.pupdevices.ColorSensor`.
