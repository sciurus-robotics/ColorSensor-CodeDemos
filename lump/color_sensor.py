"""ColorSensor on an extension port of a FloorPro, read over LUMP (LEGO hubs,
Pybricks).

Over LUMP the FloorPro reports its extension ports inside its mode-0 message:
one 5-byte pack per port (bytes 6..10 for EXT1, 11..15 for EXT2), each
``[data:4][status:1]``. For the colour sensor the data bytes are red, green,
blue scaled to 8 bit and the illumination LED level in percent; the status byte
carries the sensor type in bits 0-1 (1 = colour sensor), "saturated" in bit 2,
an error flag in bit 3 and "stale" in bit 4.

This driver talks to the FloorPro directly as a ``PUPDevice``, so no other code
is needed next to it. If your program also uses the FloorPro line-sensor driver
on the same port, both objects address the same device; the reads retry on the
occasional ``OSError`` that concurrent access to one PUPDevice can raise.
"""

from pybricks.iodevices import PUPDevice
from pybricks.parameters import Color
from pybricks.tools import wait

try:
    from math import cos, radians, sin
except ImportError:  # pragma: no cover
    from umath import cos, radians, sin  # type: ignore


def _distance_heuristic(m, c):
    """Pybricks' matcher for idealized candidates (saturated colours or greys)."""
    hue_dist = abs(c.h - m.h)
    if hue_dist > 180:
        hue_dist = 360 - hue_dist
    value_dist = abs(c.v - m.v)
    grayscale = c.s == 0 and c.h == 0
    if m.s <= 40 or m.v <= 1:
        return value_dist if grayscale else 1000 + hue_dist
    return 1000 + value_dist if grayscale else hue_dist


def _distance_bicone(a, b):
    """Pybricks' squared distance in the HSV bicone, for realistic candidates."""
    ra = a.v * a.s
    rb = b.v * b.s
    dz = (200 - b.s) * b.v - (200 - a.s) * a.v
    dx = rb * cos(radians(b.h)) - ra * cos(radians(a.h))
    dy = rb * sin(radians(b.h)) - ra * sin(radians(a.h))
    return dx * dx + dy * dy + dz * dz


class ColorSensor(PUPDevice):
    EXT1 = 1
    EXT2 = 2

    _TYPE_MASK = 0b11
    _TYPE_COLOR = 0b01
    _SAT_MASK = 1 << 2
    _ERR_MASK = 1 << 3
    _STALE_MASK = 1 << 4

    def __init__(self, port, ext_port=EXT1):
        """ColorSensor(port, ext_port=ColorSensor.EXT1)

        port: hub port of the FloorPro; ext_port: the extension port the
        colour sensor is plugged into (1 or 2). Raises ValueError if that port
        does not report a colour sensor.
        """
        super().__init__(port)
        if ext_port not in (self.EXT1, self.EXT2):
            raise ValueError("ext_port must be 1 or 2")
        self.ext_port = ext_port
        self._mode0_len = self.info()["modes"][0][1]
        self._colors = (Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE, Color.WHITE, Color.NONE)

    # --- low level ---------------------------------------------------------

    async def _read_mode0(self):
        for attempt in range(10):
            try:
                return await self.read(0)
            except OSError:
                if attempt == 9:
                    raise
                await wait(10)

    async def _send_cmd(self, msg):
        data = [ord(c) for c in msg]
        if len(data) > self._mode0_len:
            raise ValueError("command too long")
        data += [0] * (self._mode0_len - len(data))
        for attempt in range(10):
            try:
                await self.write(0, data)
                return
            except OSError:
                if attempt == 9:
                    raise
                await wait(10)

    async def data(self):
        """The 5-byte extension pack ``(r, g, b, led, status)`` of the sensor's port."""
        end = 16 - 5 if self.ext_port == self.EXT1 else 16
        raw = (await self._read_mode0())[end - 5:end]
        pack = tuple(b & 0xFF for b in raw)
        if (pack[4] & self._TYPE_MASK) != self._TYPE_COLOR:
            raise ValueError("extension port %d does not report a colour sensor" % self.ext_port)
        return pack

    # --- readings ------------------------------------------------------------

    async def rgb(self):
        """(red, green, blue), each 0 .. 255."""
        pack = await self.data()
        return pack[0], pack[1], pack[2]

    async def light(self):
        """Illumination LED level in percent, as the sensor reports it."""
        return (await self.data())[3]

    async def hsv(self):
        """The colour as a Color: hue 0 .. 359, saturation and value 0 .. 100."""
        r, g, b = await self.rgb()
        mx = max(r, g, b)
        mn = min(r, g, b)
        chroma = mx - mn
        h = 0
        s = 0
        if chroma > 0:
            if mx == r:
                h = 60 * (g - b) / chroma
            elif mx == g:
                h = 60 * (b - r) / chroma + 120
            else:
                h = 60 * (r - g) / chroma + 240
            if h < 0:
                h += 360
            s = 100 * chroma // mx
        return Color(int(h) % 360, s, 100 * mx // 255)

    async def color(self):
        """The nearest of the detectable colours (default: red, yellow, green,
        blue, white, none), matched like pybricks.pupdevices.ColorSensor."""
        m = await self.hsv()
        distance = _distance_heuristic
        for c in self._colors:
            if not ((c.s == 0 and c.h == 0) or (c.s == 100 and c.v == 100)):
                distance = _distance_bicone
                break
        best = None
        best_cost = None
        for c in self._colors:
            cost = distance(m, c)
            if best_cost is None or cost < best_cost:
                best, best_cost = c, cost
        return best

    def detectable_colors(self, colors=None):
        """Set (or, with no argument, get) the colours color() chooses from."""
        if colors is None:
            return self._colors
        self._colors = tuple(colors)

    async def saturated(self):
        """True while a colour channel is at full scale (reduce the light)."""
        return bool((await self.data())[4] & self._SAT_MASK)

    async def error(self):
        """True while the sensor reports no valid data."""
        return bool((await self.data())[4] & self._ERR_MASK)

    # --- commands ------------------------------------------------------------

    async def set_light(self, percent):
        """Illumination LED duty 0 .. 100; the sensor stores it."""
        await self._send_cmd("LED%d=%d" % (self.ext_port, int(percent)))
        for _ in range(20):
            await wait(50)
            if await self.light() == int(percent):
                return
