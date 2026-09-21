# ColorSensor — Code Demos

Driver code and demo programs for the **ColorSensor** by Sciurus Robotics: a
TCS3400 red / green / blue / clear sensor with its own illumination LED, plugged
into an extension port of the [FloorPro](https://github.com/sciurus-robotics/FloorPro-CodeDemos)
line sensor.

Product information, documentation and firmware downloads: **https://sciro.ch**

## Which folder is yours?

| Your hub | Protocol | Folder |
|---|---|---|
| LEGO Prime / Inventor hub with Pybricks | LUMP (LEGO UART sensor protocol) | [`lump/`](lump/) |
| PeakHub | PUMP (Power UART Multiplex Protocol) | [`pump/`](pump/) |

Over LUMP the colour rides inside the FloorPro's sensor message as 8-bit red,
green, blue plus the LED level; over PUMP it is a stream of its own with the
raw 16-bit readings and adjustable gain and integration time. Both folders
show the colour as hue / saturation / value and as the nearest named colour,
the way `pybricks.pupdevices.ColorSensor` does.

## Requirements

- `lump/`: [Pybricks](https://pybricks.com) firmware on the LEGO hub and
  [`pybricksdev`](https://github.com/pybricks/pybricksdev) to run scripts.
- `pump/`: a PeakHub and the [`scirodev`](https://pypi.org/project/scirodev/)
  package (`pip install scirodev`).

## License

MIT, see [LICENSE](LICENSE).
