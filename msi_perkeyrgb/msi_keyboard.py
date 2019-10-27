import os
import random
import json
from .config import KeyBlock
from .protocol_data.msi_keymaps import AVAILABLE_MSI_KEYMAPS
from .protocol_data.keycodes import REGION_KEYCODES
from .protocol_data.presets_index import PRESETS_FILES
from .hidapi_wrapping import HID_Keyboard
from .msiprotocol import make_key_colors_packet, make_refresh_packet, make_effect_packet


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

                presets_path = os.path.join(os.path.dirname(__file__),
                                            'protocol_data',
                                            'presets',
                                            filename)
                with open(presets_path) as f:
                    msi_presets = json.load(f)

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
