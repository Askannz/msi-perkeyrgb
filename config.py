from os.path import expanduser, join, exists
import re
from msi_keyboard import MSI_KEYMAP

CONFIG_FOLDER = "~/.config/msi-perkeyrgb/keyboard_configs/"
ALIASES = {}  # TODO


class ConfigError(Exception):
    pass


class ConfigParseError(ConfigError):
    pass


class LineParseError(ConfigParseError):
    pass


def load_config(config_name):

    config_path = join(expanduser(CONFIG_FOLDER), config_name)

    if not exists(config_path):
        raise ConfigError("Configuration file %s does not exist." % config_path)
    else:
        try:
            f = open(config_path, "r")
            colors_map = parse_config(f)
            f.close()
        except IOError as e:
            raise ConfigError("Error reading configuration file %s : %s" % (config_path, str(e)))
        else:
            return colors_map


def parse_config(f):

    colors_map = {}

    for i, line in enumerate(f):

        line = line.replace("\n", "")

        parameters = list(filter(None, line.split(' ')))
        if len(parameters) == 0:
            continue
        elif len(parameters) > 3:
            raise ConfigParseError("Error parsing line %d : Invalid number of parameters (expected 3, got %d)" % (i+1, len(parameters)))
        else:

            try:
                keycodes = parse_keycodes(parameters[0])
                parse_mode(parameters[1])
                color = parse_color(parameters[2])
            except LineParseError as e:
                raise ConfigParseError("Error parsing line %d : %s" % (i+1, str(e)))
            else:
                colors_map = update_colors_map(colors_map, keycodes, color)

    return colors_map


def parse_keycodes(keys_parameter):

    keycodes = []

    keys_ranges_list = keys_parameter.split(',')
    for key_str in keys_ranges_list:

        # Alias substitution
        if key_str in ALIASES.keys():
            key_str = ALIASES[key_str]

        # Parsing
        if re.fullmatch("^[0-9]+$", key_str):  # Single keycode
            keycode = int(key_str)
            if keycode not in MSI_KEYMAP.keys():
                raise LineParseError("%s is not a valid keycode." % key_str)
            else:
                keycodes.append(keycode)
        elif re.fullmatch("^[0-9]+-[0-9]+$", key_str):  # Keycode range
            keycode_1, keycode_2 = [int(s) for s in key_str.split('-')]
            if keycode_2 <= keycode_1 or keycode_1 not in MSI_KEYMAP.keys() or keycode_2 not in MSI_KEYMAP.keys():
                raise LineParseError("%s is not a valid keycode range." % key_str)
            else:
                new_keycodes = [k for k in range(keycode_1, keycode_2+1) if k in MSI_KEYMAP.keys()]
                keycodes += new_keycodes
        else:
            raise LineParseError("%s is not a keycode, nor a keycode range, nor an alias." % key_str)

    return keycodes


# This is a stub because there is only one mode for now. Will be modified in future versions.
def parse_mode(mode_parameter):

    if mode_parameter != "steady":
        raise LineParseError("Unknown mode %s" % mode_parameter)


def parse_color(color_parameter):

    if re.fullmatch("^[0-9a-f]{6}$", color_parameter):  # Color in HTML notation
        color = [int(color_parameter[i:i+2], 16) for i in [0, 2, 4]]
        return color
    else:
        raise LineParseError("%s is not a valid color" % color_parameter)


def update_colors_map(colors_map, keycodes, color):

    for k in keycodes:
        colors_map[k] = color

    return colors_map
