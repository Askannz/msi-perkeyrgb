from time import sleep
from os.path import exists
from os import popen
import ctypes as ct
import re
from msi_perkeyrgb.hidapi_types import set_hidapi_types

DELAY = 0.01


class HIDLibraryError(Exception):
    pass


class HIDNotFoundError(Exception):
    pass


class HIDOpenError(Exception):
    pass


class HIDSendError(Exception):
    pass


class HID_Keyboard:

    def __init__(self, id_str):

        # Locating HIDAPI library
        s = popen("ldconfig -p").read()
        path_matches = re.findall("/.*libhidapi-hidraw\\.so", s)
        if len(path_matches) == 0:
            raise HIDLibraryError("Cannot locate libhidapi-hidraw.so")

        lib_path = path_matches[0]

        if not exists(lib_path):
            raise HIDLibraryError("ldconfig reports HIDAPI library at %s but file does not exists." % lib_path)

        # Loading HIDAPI library
        self._hidapi = ct.cdll.LoadLibrary(lib_path)
        set_hidapi_types(self._hidapi)

        # Checking if the USB device corresponding to the keyboard exists
        s = popen("lsusb").read()
        if s.find(id_str) == -1:
            raise HIDNotFoundError

        vid, pid = [int(s, 16) for s in id_str.split(':')]
        self._device = self._hidapi.hid_open(vid, pid, ct.c_wchar_p(0))

        if self._device is None:
            raise HIDOpenError

    def send_feature_report(self, data):

        ret = self._hidapi.hid_send_feature_report(self._device, bytes(data), len(data))
        sleep(DELAY)  # The RGB controller derps if commands are sent too fast.

        if ret == -1 or ret != len(data):
            raise HIDSendError("HIDAPI returned error upon sending feature report to keyboard.")

    def send_output_report(self, data):

        ret = self._hidapi.hid_write(self._device, bytes(data), len(data))
        sleep(DELAY)

        if ret == -1 or ret != len(data):
            raise HIDSendError("HIDAPI returned error upon sending output report to keyboard.")
