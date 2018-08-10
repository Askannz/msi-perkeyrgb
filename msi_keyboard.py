import random
from hidapi_wrapping import HID_Keyboard
from protocol import make_key_colors_packet, make_refresh_packet

MSI_KEYMAP = {38: 4, 56: 5, 54: 6, 40: 7, 26: 8, 41: 9, 42: 10, 43: 11, 31: 12, 44: 13, 45: 14, 46: 15, 58: 16, 57: 17, 32: 18, 33: 19, 24: 20, 27: 21, 39: 22, 28: 23, 30: 24, 55: 25, 25: 26, 53: 27, 29: 28, 52: 29, 10: 30, 11: 31, 12: 32, 13: 33, 14: 34, 15: 35, 16: 36, 17: 37, 18: 38, 19: 39, 67: 58, 68: 59, 69: 60, 70: 61, 71: 62, 72: 63, 36: 40, 51: 49, 94: 100, 9: 41, 22: 42, 23: 43, 65: 44, 20: 45, 21: 46, 34: 47, 35: 48, 47: 51, 48: 52, 49: 53, 59: 54, 60: 55, 61: 56, 66: 57, 37: 224, 50: 225, 64: 226, 133: 227, 105: 228, 62: 229, 108: 230, 73: 64, 74: 65, 75: 66, 76: 67, 95: 68, 96: 69, 107: 70, 78: 71, 127: 72, 118: 73, 112: 75, 119: 76, 117: 78, 114: 79, 113: 80, 116: 81, 111: 82, 77: 83, 106: 84, 63: 85, 82: 86, 86: 87, 104: 88, 87: 89, 88: 90, 89: 91, 83: 92, 84: 93, 85: 94, 79: 95, 80: 96, 81: 97, 90: 98, 91: 99, 'fn': 240}
REGION_KEYCODES = {"alphanum": [0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f],
                   "enter": [0x28, 0x31, 0x32, 0x64, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x90, 0x91, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                   "modifiers": [0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x65, 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                   "numpad": [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f, 0x60, 0x61, 0x62, 0x63, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}


class MSI_Keyboard:

    def __init__(self):

        self._hid_keyboard = HID_Keyboard()

    def set_color_all(self, color):

        for region in REGION_KEYCODES.keys():

            keycodes = REGION_KEYCODES[region]
            n = len(keycodes)
            colors_values = [color] * n
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_random_color_all(self):

        for region in REGION_KEYCODES.keys():

            keycodes = REGION_KEYCODES[region]
            n = len(keycodes)
            colors_values = []
            for i in range(n):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                colors_values.append([r, g, b])
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_colors(self, linux_colors_map):

        # Translating from Linux keycodes to MSI's own encoding
        linux_keycodes = linux_colors_map.keys()
        colors = linux_colors_map.values()
        msi_keycodes = [MSI_KEYMAP[k] for k in linux_keycodes]
        msi_colors_map = dict(zip(msi_keycodes, colors))

        # Sorting requested keycodes by keyboard region
        maps_sorted_by_region = {}

        for keycode in msi_colors_map.keys():
            for region in REGION_KEYCODES.keys():
                if keycode in REGION_KEYCODES[region]:
                    if region not in maps_sorted_by_region.keys():
                        maps_sorted_by_region[region] = {}
                    maps_sorted_by_region[region][keycode] = msi_colors_map[keycode]

        # Sending color commands by region
        for region, region_colors_map in maps_sorted_by_region.items():
            key_colors_packet = make_key_colors_packet(region, region_colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def refresh(self):

        refresh_packet = make_refresh_packet()
        self._hid_keyboard.send_output_report(refresh_packet)
