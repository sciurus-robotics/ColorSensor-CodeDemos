from pybricks.hubs import InventorHub
from pybricks.parameters import Port, Button
from pybricks.tools import wait, run_task, multitask
from floor_pro_v3 import FloorProV3
from sr_lp_cs_ext import ColorSensorExt

PORT = Port.A
# Use EXT1 for the extension sensor data (modes 11-15)
EXT_PORT = FloorProV3.EXT1

floor_pro = FloorProV3(port=PORT)
lp_cs_ext = ColorSensorExt(pup_device=floor_pro, ext_port=EXT_PORT)

hub = InventorHub()


async def show_data_loop():
    while True:
        data = await lp_cs_ext.data()
        print("Sensor Raw data:", data)
        print("Sensor Values:", await lp_cs_ext.str())
        await wait(400)


async def calibration_loop():
    while True:
        print(
            f"Press RIGHT to start calibration of extension port {EXT_PORT}.")
        while True:
            if Button.RIGHT in hub.buttons.pressed():
                break
            else:
                await wait(250)
        await lp_cs_ext.calibration_start()
        print(
            f"Calibration started. Press LEFT to stop calibration of extension port {EXT_PORT}.")
        while True:
            if Button.LEFT in hub.buttons.pressed():
                break
            else:
                await wait(250)
        await lp_cs_ext.calibration_stop()

        if await lp_cs_ext.calibration_weak():
            print(
                "WARN calibration is weak and will not be applied. Consider recalibrating.")

run_task(multitask(calibration_loop(), show_data_loop(), race=True))
