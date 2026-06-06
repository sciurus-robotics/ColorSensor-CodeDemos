from pybricks.tools import wait
from floor_pro_v3 import FloorProV3


class ColorSensorExt:
    TCSCALIBSTART = "TCSCALIBSTART"
    TCSCALIBSTOP = "TCSCALIBSTOP"

    TCSCALIBCLEAR = "TCSCALIBCLEAR"

    TYPE_MASK = 0b11
    TYPE_TCS = 0b01

    CALIB_RUNNING_MASK = 1 << 7
    CALIB_RUNNING = 1 << 7

    CAL_CLEAR_MASK = 1 << 5
    CAL_CLEAR = 1 << 5

    CALIB_WEAK_MASK = 1 << 6
    CALIB_WEAK = 1 << 6

    def __init__(self, pup_device: FloorProV3, ext_port=1):
        # TODO we require FloorProV3 at this time because it is currently the only PUPDevice that supports the necessary ext_port_data() method;
        # this should be more generic or just rely on duck typing entirely
        self.pup_device = pup_device
        if ext_port not in (1, 2):
            raise ValueError("ext_port must be 1 or 2")
        self.ext_port = ext_port

    async def data(self):
        data = await self.pup_device.ext_port_data(self.ext_port)
        if (data[4] & self.TYPE_MASK) != self.TYPE_TCS:
            raise ValueError(
                f"Data from extension port {self.ext_port} does not match expected TCS sensor format.")
        return data

    async def rgbled(self):
        """ Returns a tuple of (R, G, B, LED) values as 8-bit unsigned integers (0 to 255) from the extension port. """
        data = await self.data()
        return tuple(data[i] for i in range(4))

    async def hsv(self):
        """ Returns a tuple of (H, S, V) with H in 0..360 and S/V in 0..100 from the extension port. """
        r, g, b, _ = await self.rgbled()
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        delta = max_c - min_c

        # Calculate Hue
        if delta == 0:
            h = 0
        elif max_c == r:
            h = (60 * ((g - b) / delta) + 360) % 360
        elif max_c == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        else:  # max_c == b
            h = (60 * ((r - g) / delta) + 240) % 360

        # Calculate Saturation
        s = 0 if max_c == 0 else (delta / max_c) * 100

        # Value is the maximum RGB component scaled to 0..100
        v = (max_c / 255) * 100

        return int(round(h)), int(round(s)), int(round(v))

    async def str(self):
        data = await self.data()
        hsv = await self.hsv()
        return f"ColorSensorExt(ext_port={self.ext_port}, R={data[0]}, G={data[1]}, B={data[2]}, LED={data[3]}, {data[4]:08b})" + f", HSV=({hsv[0]}, {hsv[1]}, {hsv[2]})"

    async def calibration_start(self):
        """ Start the sensor calibration process for the extension port. """
        while (await self.data())[4] & self.CALIB_RUNNING_MASK != self.CALIB_RUNNING:
            await self.pup_device.send_cmd(self.TCSCALIBSTART + str(self.ext_port))
            await wait(50)

    async def calibration_stop(self):
        """ Stop the sensor calibration process for the extension port. """
        while (await self.data())[4] & self.CALIB_RUNNING_MASK == self.CALIB_RUNNING:
            await self.pup_device.send_cmd(self.TCSCALIBSTOP + str(self.ext_port))
            await wait(50)

    async def calibration_clear(self):
        """ Clear any saved calibration data. """
        while (await self.data())[4] & self.CAL_CLEAR_MASK != self.CAL_CLEAR:
            await self.pup_device.send_cmd(self.TCSCALIBCLEAR + str(self.ext_port))
            await wait(50)

    async def calibration_weak(self) -> bool:
        """ Returns True if the sensor is currently in a weakly calibrated state, False otherwise. """
        data = await self.data()
        return (data[4] & self.CALIB_WEAK_MASK) == self.CALIB_WEAK
