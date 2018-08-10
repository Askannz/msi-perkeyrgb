from time import sleep
import ctypes as ct
from hidapi_types import set_hidapi_types

DELAY = 0.01
VENDOR_ID = 0x1038
PRODUCT_ID = 0x1122


class HID_Keyboard:

    def __init__(self, vid=VENDOR_ID, pid=PRODUCT_ID):

        self._hidapi = ct.cdll.LoadLibrary('/usr/lib/libhidapi-hidraw.so')
        set_hidapi_types(self._hidapi)

        self._device = self._hidapi.hid_open(vid, pid, ct.c_wchar_p(0))

        if self._device == 0:

            print("Cannot open keyboard. Please execute this program \
                  as root or give yourself read/write permissions to /dev/hidraw0.")
            raise RuntimeError("Cannot open keyboard.")

    def send_feature_report(self, data):

        ret = self._hidapi.hid_send_feature_report(self._device, bytes(data), len(data))
        sleep(DELAY)

        if ret == -1 or ret != len(data):
            raise RuntimeError("HIDAPI returned error upon sending feature report to keyboard.")

    def send_output_report(self, data):

        ret = self._hidapi.hid_write(self._device, bytes(data), len(data))
        sleep(DELAY)

        if ret == -1 or ret != len(data):
            raise RuntimeError("HIDAPI returned error upon sending output report to keyboard.")
