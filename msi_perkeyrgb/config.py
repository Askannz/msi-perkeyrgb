import re
import sys

ALIAS_ALL = "all"
ALIASES = {ALIAS_ALL: "9-133,fn",
           "f_row": "67-76,95,96",
           "arrows": "111,113,114,116",
           "num_row": "10-21",
           "numpad": "63,77,79-91,104,106",
           "characters": "24-35,38-48,52-61,65"}


class ConfigError(Exception):
    pass


class ConfigParseError(Exception):
    pass


class LineParseError(Exception):
    pass


class UnknownModelError(Exception):
    pass


def load_config(config_path, msi_keymap):
    try:
        if config_path == '-':
            f = sys.stdin
        else:
            f = open(config_path, "r")
        config_map = parse_config(f, msi_keymap)
        f.close()
    except IOError as e:
        raise ConfigError("IOError : %s" % str(e)) from e
        pass
    except FileNotFoundError as e:
        raise ConfigError("File %s does not exist" % config_path) from e
        pass
    except ConfigParseError as e:
        raise ConfigError("Parsing error : %s" % str(e)) from e
        pass
    except UnknownModelError as e:
        raise e
    except Exception as e:
        raise ConfigError("Unknown error : %s" % str(e)) from e
        pass
    else:
        return config_map


def load_steady(color, msi_keymap):
    """Setup the key map to be all a steady color
    """
    colors_map = {}
    warnings = []

    try:
        keycodes = parse_keycodes(msi_keymap, ALIAS_ALL)
        color = parse_color(color)
    except LineParseError as e:
        raise ConfigParseError("Color parse error %s" % str(e)) from e
        pass
    else:
        colors_map = update_colors_map(colors_map, keycodes, color)

    return colors_map, warnings


def parse_config(f, msi_keymap):

    colors_map = {}
    warnings = []

    for i, line in enumerate(f):

        line = line.replace("\n", "")

        if line.replace(" ", "")[0] == "#":
            continue

        parameters = list(filter(None, line.split(' ')))

        if i == 0 and parameters[0] == "model":
            warnings += ["Passing the laptop model in the configuration file is deprecated, use the --model option instead."]
            continue

        # Parsing a keys/color line
        if len(parameters) == 0:
            continue
        elif len(parameters) > 3:
            raise ConfigParseError("line %d : Invalid number of parameters (expected 3, got %d)" % (i+1, len(parameters)))
        else:

            try:
                keycodes = parse_keycodes(msi_keymap, parameters[0])
                parse_mode(parameters[1])
                color = parse_color(parameters[2])
            except LineParseError as e:
                raise ConfigParseError("line %d : %s" % (i+1, str(e))) from e
                pass
            else:
                colors_map = update_colors_map(colors_map, keycodes, color)

    return colors_map, warnings


def parse_keycodes(msi_keymap, keys_parameter):

    keycodes = []

    # Alias substitution
    for alias in ALIASES.keys():
        keys_parameter = keys_parameter.replace(alias, ALIASES[alias])

    keys_ranges_list = keys_parameter.split(',')
    for key_str in keys_ranges_list:

        # Parsing
        if re.fullmatch("^fn$", key_str):  # Special keycode "fn"
            keycodes.append("fn")
        elif re.fullmatch("^[0-9]+$", key_str):  # Single keycode
            keycode = int(key_str)
            if keycode not in msi_keymap.keys():
                raise LineParseError("%s is not a valid keycode." % key_str)
            else:
                keycodes.append(keycode)
        elif re.fullmatch("^[0-9]+-[0-9]+$", key_str):  # Keycode range
            keycode_1, keycode_2 = [int(s) for s in key_str.split('-')]
            if keycode_2 <= keycode_1 or keycode_1 not in msi_keymap.keys() or keycode_2 not in msi_keymap.keys():
                raise LineParseError("%s is not a valid keycode range." % key_str)
            else:
                new_keycodes = [k for k in range(keycode_1, keycode_2+1) if k in msi_keymap.keys()]
                keycodes += new_keycodes
        else:
            raise LineParseError("%s is not a keycode, nor a keycode range, nor an alias." % key_str)

    return keycodes


# This is a stub because there is only one mode for now. Will be modified in future versions.
def parse_mode(mode_parameter):

    if mode_parameter != "steady":
        raise LineParseError("Unknown mode %s" % mode_parameter)


def parse_color(color_parameter):

    if re.fullmatch("^[0-9a-f]{6}$", color_parameter.lower()):  # Color in HTML notation
        color = [int(color_parameter[i:i+2], 16) for i in [0, 2, 4]]
        return color
    else:
        raise LineParseError("%s is not a valid color" % color_parameter)


def update_colors_map(colors_map, keycodes, color):

    for k in keycodes:
        colors_map[k] = color

    return colors_map
