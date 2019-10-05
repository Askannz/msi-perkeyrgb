import os
import random
import json
from msi_perkeyrgb.config import KeyBlock, Transition, MsiEffect
from msi_perkeyrgb.hidapi_wrapping import HID_Keyboard
from msi_perkeyrgb.msiprotocol import make_key_colors_packet, make_refresh_packet, make_effect_packet

AVAILABLE_MSI_KEYMAPS = [
             (["GE63", "GE73", "GE75", "GS63", "GS73", "GS75", "GX63", "GT63", "GL63"],
             {"fn": 0xf0, 38: 0x4, 56: 0x5, 54: 0x6, 40: 0x7, 26: 0x8, 41: 0x9, 42: 0xa, 43: 0xb, 31: 0xc, 44: 0xd, 45: 0xe, 46: 0xf, 58: 0x10, 57: 0x11, 32: 0x12, 33: 0x13, 24: 0x14, 27: 0x15, 39: 0x16, 28: 0x17, 30: 0x18, 55: 0x19, 25: 0x1a, 53: 0x1b, 29: 0x1c, 52: 0x1d, 10: 0x1e, 11: 0x1f, 12: 0x20, 13: 0x21, 14: 0x22, 15: 0x23, 16: 0x24, 17: 0x25, 18: 0x26, 19: 0x27, 67: 0x3a, 68: 0x3b, 69: 0x3c, 70: 0x3d, 71: 0x3e, 72: 0x3f, 36: 0x28, 51: 0x31, 94: 0x64, 9: 0x29, 22: 0x2a, 23: 0x2b, 65: 0x2c, 20: 0x2d, 21: 0x2e, 34: 0x2f, 35: 0x30, 47: 0x33, 48: 0x34, 49: 0x35, 59: 0x36, 60: 0x37, 61: 0x38, 66: 0x39, 37: 0xe0, 50: 0xe1, 64: 0xe2, 133: 0xe3, 105: 0xe4, 62: 0xe5, 108: 0xe6, 73: 0x40, 74: 0x41, 75: 0x42, 76: 0x43, 95: 0x44, 96: 0x45, 107: 0x46, 78: 0x47, 127: 0x48, 118: 0x49, 112: 0x4b, 119: 0x4c, 117: 0x4e, 114: 0x4f, 113: 0x50, 116: 0x51, 111: 0x52, 77: 0x53, 106: 0x54, 63: 0x55, 82: 0x56, 86: 0x57, 104: 0x58, 87: 0x59, 88: 0x5a, 89: 0x5b, 83: 0x5c, 84: 0x5d, 85: 0x5e, 79: 0x5f, 80: 0x60, 81: 0x61, 90: 0x62, 91: 0x63}),
             (["GS65"],
             {"fn": 0xf0, 38: 0x4, 56: 0x5, 54: 0x6, 40: 0x7, 26: 0x8, 41: 0x9, 42: 0xa, 43: 0xb, 31: 0xc, 44: 0xd, 45: 0xe, 46: 0xf, 58: 0x10, 57: 0x11, 32: 0x12, 33: 0x13, 24: 0x14, 27: 0x15, 39: 0x16, 28: 0x17, 30: 0x18, 55: 0x19, 25: 0x1a, 53: 0x1b, 29: 0x1c, 52: 0x1d, 10: 0x1e, 11: 0x1f, 12: 0x20, 13: 0x21, 14: 0x22, 15: 0x23, 16: 0x24, 17: 0x25, 18: 0x26, 19: 0x27, 67: 0x3a, 68: 0x3b, 69: 0x3c, 70: 0x3d, 71: 0x3e, 72: 0x3f, 36: 0x28, 51: 0x31, 94: 0x64, 9: 0x29, 22: 0x2a, 23: 0x2b, 65: 0x2c, 20: 0x2d, 21: 0x2e, 34: 0x2f, 35: 0x30, 47: 0x33, 48: 0x34, 49: 0x35, 59: 0x36, 60: 0x37, 61: 0x38, 66: 0x39, 37: 0xe0, 50: 0xe1, 64: 0xe2, 133: 0xe3, 105: 0xe4, 62: 0xe5, 108: 0xe6, 73: 0x40, 74: 0x41, 75: 0x42, 76: 0x43, 95: 0x44, 96: 0x45, 107: 0x46, 78: 0x47, 127: 0x48, 118: 0x49, 112: 0x4b, 119: 0x4c, 117: 0x4e, 114: 0x4f, 113: 0x50, 116: 0x51, 111: 0x52, 77: 0x53, 106: 0x54, 63: 0x55, 82: 0x56, 86: 0x57, 104: 0x58, 87: 0x59, 88: 0x5a, 89: 0x5b, 83: 0x5c, 84: 0x5d, 85: 0x5e, 79: 0x5f, 80: 0x60, 81: 0x61, 90: 0x62, 91: 0x63, 110: 0x4a, 115: 0x4d})
             ]
REGION_KEYCODES = {"alphanum": [0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f],
                   "enter": [0x28, 0x31, 0x32, 0x64, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x90, 0x91, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                   "modifiers": [0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x65, 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                   "numpad": [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f, 0x60, 0x61, 0x62, 0x63, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}

PRESETS_FILES = [
             (["GE63", "GE73", "GE75", "GS63", "GS73", "GS75", "GX63", "GT63", "GL63"], "1.json"),
             (["GS65"], "2.json")
             ]


class MSI_Keyboard:

    @staticmethod
    def get_model_keymap(msi_model):
        for msi_models, msi_keymap in AVAILABLE_MSI_KEYMAPS:
            if msi_model in msi_models:
                return msi_keymap

    @staticmethod
    def get_model_presets(msi_model):

        for msi_models, filename in PRESETS_FILES:
            if msi_model in msi_models:
                presets_path = os.path.join(os.path.dirname(__file__), 'presets', filename)
                f = open(presets_path)
                msi_presets = json.load(f)
                f.close()
                return msi_presets

    def __init__(self, usb_id, msi_keymap, msi_presets):

        self._hid_keyboard = HID_Keyboard(usb_id)
        self._msi_keymap = msi_keymap
        self._msi_presets = msi_presets

    def set_color_all(self, color):

        for region in REGION_KEYCODES.keys():

            keycodes = REGION_KEYCODES[region]
            n = len(keycodes)
            colors_values = [KeyBlock(color, "", 1) ] * n
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map, None)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_random_color_all(self, color):

        for region in REGION_KEYCODES.keys():

            keycodes = REGION_KEYCODES[region]
            n = len(keycodes)
            colors_values = []
            for i in range(n):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                colors_values.append(KeyBlock([r, g, b], "", 1))
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map, None)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_effect_all(self, effect_map, effect_name):
        for region in REGION_KEYCODES.keys():

            keycodes = REGION_KEYCODES[region]
            n = len(keycodes)
            colors_values = []

            colors_values = [KeyBlock([0x00, 0x00, 0x00], effect_name, 0)] * n
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map, effect_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_colors(self, linux_colors_map, effect_map):

        # Translating from Linux keycodes to MSI's own encoding
        linux_keycodes = linux_colors_map.keys()
        keyblocks = linux_colors_map.values()
        msi_keycodes = [self._msi_keymap[k] for k in linux_keycodes]
        msi_colors_map = dict(zip(msi_keycodes, keyblocks))

        # Sorting requested keycodes by keyboard region
        maps_sorted_by_region = {}
        for keycode in msi_colors_map.keys():
            for region in REGION_KEYCODES.keys():
                if keycode in REGION_KEYCODES[region]:
                    if region not in maps_sorted_by_region.keys():
                        maps_sorted_by_region[region] = {}
                    maps_sorted_by_region[region][keycode] = msi_colors_map[keycode]

        # Sending effect commands
        if effect_map is not None:
            for effect, effect_objects in effect_map.items():
                effect_packet = make_effect_packet(effect_objects)
                self._hid_keyboard.send_feature_report(effect_packet)

        # Sending color commands by region
        for region, region_colors_map in maps_sorted_by_region.items():
            key_colors_packet = make_key_colors_packet(region, region_colors_map, effect_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_preset(self, preset):

        feature_reports_list = self._msi_presets[preset]
        for data in feature_reports_list:
            self._hid_keyboard.send_feature_report(bytearray.fromhex(data))

    def refresh(self):

        refresh_packet = make_refresh_packet()
        self._hid_keyboard.send_output_report(refresh_packet)
