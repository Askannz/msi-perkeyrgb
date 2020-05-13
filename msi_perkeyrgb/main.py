#!/usr/bin/env python

import sys
import argparse
import webcolors
import colorsys
import random
from .protocol_data.msi_keymaps import AVAILABLE_MSI_KEYMAPS
from .config import load_config, load_steady, ConfigError
from .parsing import parse_model, parse_usb_id, parse_preset, UnknownModelError, UnknownIdError, UnknownPresetError
from .msi_keyboard import MSI_Keyboard
from .hidapi_wrapping import HIDLibraryError, HIDNotFoundError, HIDOpenError

VERSION = "2.1"
DEFAULT_ID = "1038:1122"
DEFAULT_MODEL = "GE63"  # Default laptop model if nothing specified


def main():
    parser = argparse.ArgumentParser(description='Tool to control per-key RGB keyboard backlighting on MSI laptops. https://github.com/Askannz/msi-perkeyrgb')
    parser.add_argument('-v', '--version', action='store_true', help='Prints version and exits.')
    parser.add_argument('-c', '--config', action='store', metavar='FILEPATH', help='Loads the configuration file located at FILEPATH. Refer to the README for syntax. If set to "-", '
                                                                                    'the configuration file is read from the standard input (stdin) instead.')
    parser.add_argument('-d', '--disable', action='store_true', help='Disable RGB lighting.')
    parser.add_argument('--id', action='store', metavar='VENDOR_ID:PRODUCT_ID', help='This argument allows you to specify the vendor/product id of your keyboard. You should not have to use this unless opening the keyboard fails with the default value. IDs are in hexadecimal format (example :  1038:1122)')
    parser.add_argument('--list-presets', action='store_true', help='List available presets for the given laptop model.')
    parser.add_argument('-p', '--preset', action='store', help='Use vendor preset (see --list-presets).')
    parser.add_argument('-m', '--model', action='store', help='Set laptop model (see --list-models). If not specified, will use %s as default.' % DEFAULT_MODEL)
    parser.add_argument('--list-models', action='store_true', help='List available laptop models.')
    parser.add_argument('-s', '--steady', action='store', metavar='COLOR', help='Set all of keyboard to a steady hex or css3 color e.g. 00ff00 or green.')
    parser.add_argument('-r', '--random',action='store_true',help='Set all of keyboard to a random hex color.')

    args = parser.parse_args()

    if args.version:
        print("Version : %s" % VERSION)

    elif args.list_models:
        print("Available laptop models are :")
        for msi_models, _ in AVAILABLE_MSI_KEYMAPS:
            for model in msi_models:
                print(model)
        print("\nIf your laptop is not in this list, use the closest one (with a keyboard layout as similar as possible). This tool will only work with per-key RGB models.")

    else:

        # Parse laptop model
        if not args.model:
            print("No laptop model specified, using %s as default." % DEFAULT_MODEL)
            msi_model = DEFAULT_MODEL
        else:
            try:
                msi_model = parse_model(args.model)
            except UnknownModelError:
                print("Unknown MSI model : %s" % args.model)
                sys.exit(1)

        # Parse USB vendor/product ID
        if not args.id:
            usb_id = parse_usb_id(DEFAULT_ID)
        else:
            try:
                usb_id = parse_usb_id(args.id)
            except UnknownIdError:
                print("Unknown vendor/product ID : %s" % args.id)
                sys.exit(1)

        # Loading presets
        msi_presets = MSI_Keyboard.get_model_presets(msi_model)

        if args.list_presets:
            if msi_presets == {}:
                print("No presets available for %s." % msi_model)
            else:
                print("Available presets for %s:" % msi_model)
                for preset in msi_presets.keys():
                    print("\t- %s" % preset)

        else:

            # Loading keymap
            msi_keymap = MSI_Keyboard.get_model_keymap(msi_model)

            # Loading keyboard
            try:
                kb = MSI_Keyboard(usb_id, msi_keymap, msi_presets)
            except HIDLibraryError as e:
                print("Cannot open HIDAPI library : %s. Make sure you have installed libhidapi on your system, then try running \"sudo ldconfig\" to regenerate library cache." % str(e))
                sys.exit(1)
            except HIDNotFoundError:
                if not args.id:
                    print("No MSI keyboards with a known product/vendor IDs were found. However, if you think your keyboard should work with this program, you can try overriding the ID by adding the option \"--id VENDOR_ID:PRODUCT_ID\". In that case you will also need to give yourself proper read/write permissions to the corresponding /dev/hidraw* device.")
                else:
                    print("No USB device with ID %s found." % args.id)
                sys.exit(1)
            except HIDOpenError:
                print("Cannot open keyboard. Possible causes :\n- You don't have permissions to open the HID device. Run this program as root, or give yourself read/write permissions to the corresponding /dev/hidraw*. If you have just installed this tool, reboot your computer for the udev rule to take effect.\n- The USB device is not a HID device.")
                sys.exit(1)

            # If user has requested disabling
            if args.disable:
                kb.set_color_all([0, 0, 0])
                kb.refresh()

            # If user has requested a preset
            elif args.preset:
                try:
                    preset = parse_preset(args.preset, msi_presets)
                except UnknownPresetError:
                    print("Preset %s not found for model %s. Use --list-presets for available options" % (args.preset, msi_model))
                    sys.exit(1)

                kb.set_preset(preset)
                kb.refresh()

            # If user has requested to load a config file
            elif args.config:
                try:
                    colors_map, warnings = load_config(args.config, msi_keymap)
                except ConfigError as e:
                    print("Error reading config file : %s" % str(e))
                    sys.exit(1)

                for w in warnings:
                    print("Warning :", w)

                kb.set_colors(colors_map)
                kb.refresh()

            # If user has requested to display a steady color
            elif args.steady:
                try:
                    colors_map, warnings = load_steady(webcolors.name_to_hex(args.steady)[1:], msi_keymap)
                except ValueError as e:
                    try:
                        colors_map, warnings = load_steady(args.steady, msi_keymap)
                    except ConfigError as e:
                        print("Error preparing steady color : %s" % str(e))
                        sys.exit(1)
                kb.set_colors(colors_map)
                kb.refresh()

            # If user has requested to display a random color
            elif args.random:
                try:
                    # Generate random color with 25% <= luminance < 75% and 50% <= saturation < 100%
                    # these bounds were chosen arbitrarily by inspection so that
                    # the resulting random color won't be too light or dark or desaturated.
                    # 
                    # HLS was chosen instead of HVL due to being more human-friendly
                    # see https://en.wikipedia.org/wiki/HSL_and_HSV#Motivation
                    col=webcolors.PercentRGB(
                            *colorsys.hls_to_rgb(
                                random.random(),        # hue
                                random.random()*.5+.25, # lightness
                                random.random()*.5+.5   # saturation
                                )
                            )
                    colors_map, warnings = load_steady(
                            webcolors.rgb_percent_to_hex(["{:.2%}".format(val) for val in col])[1:],
                            msi_keymap
                            )
                except ConfigError as e:
                    print("Error preparing steady color : %s" % str(e))
                    sys.exit(1)
                kb.set_colors(colors_map)
                kb.refresh()

            # If user has not requested anything
            else:
                print("Nothing to do ! Please specify a preset, steady, or a config file.")


if __name__ == '__main__':
    main()
