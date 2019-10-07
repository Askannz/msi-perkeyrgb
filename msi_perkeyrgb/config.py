import re
import sys

PRESET_COLORS = {"off": [0x00, 0x00, 0x00]}
ALIAS_ALL = "all"
ALIASES = {ALIAS_ALL: "9-133,fn",
           "f_row": "67-76,95,96",
           "arrows": "111,113,114,116",
           "num_row": "10-21",
           "numpad": "63,77,79-91,104,106",
           "characters": "24-35,38-48,52-61,65"}


class MsiEffect:

    def __init__(self, ident):
        self.start_color = [0x00, 0x00, 0x00]
        self.transition_list = []
        self.period = 0
        self.identifier = ident
        self.wave_mode = False
        self.wave_origin_x = None
        self.wave_origin_y = None
        self.wave_rad_control = None
        self.wave_wavelength = None
        self.wave_direction = None


class Transition:

    def __init__(self, color, duration):
        self.color = color
        self.duration = duration


class KeyBlock:
    def __init__(self, color=PRESET_COLORS["off"], effect="", mode=-1):
        self.mode = mode
        self.effect_name = effect
        self.color = color
        self.react_color = PRESET_COLORS["off"]
        self.react_duration = 0


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
        config_map, effect_map, warnings = parse_config(f, msi_keymap)
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
        return config_map, effect_map, warnings


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
        colors_map = update_colors_map(colors_map, keycodes, "steady", color, '')

    return colors_map, warnings


def load_breathe(color, msi_keymap):
    """Set up the keymap to use a breathing animation.
    """
    colors_map = {}
    effect_map = {}
    warnings = []

    try:
        keycodes = parse_keycodes(msi_keymap, ALIAS_ALL)
        color = parse_color(color)
    except LineParseError as e:
        raise ConfigParseError("Color parse error %s" % str(e)) from e
        pass
    else:
        colors_map = update_colors_map(colors_map, keycodes, "effect", PRESET_COLORS["off"], "breathe_effect")

        # Set up the effect
        effect_map["breathe_effect"] = MsiEffect(0)
        effect_map["breathe_effect"].start_color = color
        effect_map["breathe_effect"].transition_list.append(Transition(PRESET_COLORS["off"], 500))
        effect_map["breathe_effect"].transition_list.append(Transition(color, 750))

        return colors_map, effect_map, warnings



def parse_config(f, msi_keymap):

    colors_map = {}
    warnings = []
    effect_map = {}

    in_event_block = 0
    selected_event_name = ""

    for i, line in enumerate(f):

        line = line.replace("\n", "")
        line = line.replace("\t", "")

        if line == "":
            continue

        if line.replace(" ", "")[0] == "#":
            continue

        parameters = list(filter(None, line.split(' ')))

        # Effects must be declared multi-line; therefore special parsing considerations must be made.
        if in_event_block == 1:
            if parameters[0] == "trans":
                if len(parameters) != 3:
                    raise ConfigParseError("line %d: Effect trans statement invalid (requires 3 parameters, got %d)" % (i+1, len(parameters)))

                try:
                    transition_color = parse_color(parameters[1])
                    transition_duration = int(parameters[2])

                    effect_map[selected_event_name].period = parse_time_period(transition_duration, effect_map[selected_event_name].period)
                except LineParseError as e:
                    raise ConfigParseError("line %d : %s" % (i + 1, str(e))) from e
                    pass
                else:
                    effect_add_transition(effect_map, selected_event_name, transition_color, transition_duration)
                    continue
            elif parameters[0] == "start":
                if len(parameters) != 2:
                    raise ConfigParseError("line %d: Effect start statement invalid (requires 2 parameters, got %d)" % i+1, len(parameters))
                try:
                    startcolor = parse_color(parameters[1])
                except LineParseError as e:
                    raise ConfigParseError("line %d : %s" % (i + 1, str(e))) from e
                else:
                    effect_map[selected_event_name].start_color = startcolor
                    continue
            elif parameters[0] == "wave":
                if len(parameters) != 6:
                    raise ConfigParseError("line %d: Effect wave statement invalid (requires 6 parameters)")
                try:
                    effect_map[selected_event_name].wave_mode = True

                    origin_x = verify_percentage(int(parameters[1]))
                    effect_map[selected_event_name].wave_origin_x = origin_x

                    origin_y = verify_percentage(int(parameters[2]))
                    effect_map[selected_event_name].wave_origin_y = origin_y

                    rad_control = parameters[3].lower()
                    if rad_control == "xy":
                        effect_map[selected_event_name].wave_rad_control = "xy"
                    elif rad_control == "y":
                        effect_map[selected_event_name].wave_rad_control = "y"
                    elif rad_control == "x":
                        effect_map[selected_event_name].wave_rad_control = "x"
                    else:
                        raise ConfigParseError("line %d: Parameter 'wave_direction' is not valid. (expected: \"x\", \"y\", \"xy\", got %s" % i+1, parameters[3].lower)

                    wavelength = verify_percentage(int(parameters[4]))
                    effect_map[selected_event_name].wave_wavelength = wavelength

                    direction = parameters[5].lower()
                    if direction == "in":
                        effect_map[selected_event_name].wave_direction = direction
                    elif direction == "out":
                        effect_map[selected_event_name].wave_direction = direction
                    else:
                        raise ConfigParseError("line %d: parameter \"wave_direction\" is not valid."
                                               " (expected: \"in\", \"out\", got %s)" % i+1, direction)
                except LineParseError as e:
                    raise ConfigParseError("line %d: %s" % (i + 1, str(e))) from e
                continue

            elif parameters[0] == "end":
                in_event_block = 0
                selected_event_name = ""
                continue
            else:
                raise ConfigParseError("line %d: Invalid statement in Effect block (found %s}" % i+1, line)

        if i == 0 and parameters[0] == "model":
            warnings += ["Passing the laptop model in the configuration file is deprecated, use the --model option instead."]
            continue

        if parameters[0] == "effect":
            if len(parameters) != 2:
                raise ConfigParseError("line %d: Effect declaration invalid. (expected 2 parameters, got %d)" % (i+1, len(parameters)))
                pass
            selected_event_name = parameters[1]
            effect_map[selected_event_name] = MsiEffect(len(effect_map))
            in_event_block = 1
            continue

        if i == 0 and parameters[0] == "end":
            warnings += ["Found an 'end' that doesn't correspond to an effect block."]
            continue

        # Parsing a keys/color line
        if len(parameters) == 0:
            continue
        elif len(parameters) > 3 | len(parameters):
            raise ConfigParseError("line %d : Invalid number of parameters (expected 3 or 4) got %d)" %
                                   (i+1, len(parameters)))
            pass
        else:

            try:
                effectname = None
                color_react = None
                color_react_duration = None
                color = None

                keycodes = parse_keycodes(msi_keymap, parameters[0])
                parsemode = parse_mode(parameters[1])
                if parsemode == "effect":
                    if len(parameters) == 3:
                        effectname = parameters[2]
                    else:
                        raise ConfigParseError("line %d : Invalid number of parameters (expected 3 or 5) got %d)" %
                            (i + 1, len(parameters)))

                elif parsemode == "steady":
                    if len(parameters) != 3:
                        raise ConfigParseError("line %d : Invalid number of parameters (expected 3) got %d)" %
                                               (i + 1, len(parameters)))
                    color = parse_color(parameters[2])
                elif parsemode == "reactive":
                    if len(parameters) != 5:
                        raise ConfigParseError("line %d : Invalid number of parameters for parameter 'reactive (expected 4) got %d)" %
                                               (i + 1, len(parameters)))
                    color = parse_color(parameters[2])
                    color_react = parse_color(parameters[3])
                    color_react_duration = int(parameters[4])
            except LineParseError as e:
                raise ConfigParseError("line %d : %s" % (i+1, str(e))) from e
                pass
            else:
                colors_map = update_colors_map(colors_map, keycodes, parsemode, color, effectname, color_react,
                                               color_react_duration)

    if in_event_block == 1:
        raise ConfigParseError("<EOF>: An effect block was not closed properly.")

    return colors_map, effect_map, warnings


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


# Added entry for effects; still in progress.
def parse_mode(mode_parameter):

    if mode_parameter == "steady":
        return "steady"
    elif mode_parameter == "effect":
        return "effect"
    elif mode_parameter == "reactive":
        return "reactive"
    else:
        raise LineParseError("Unknown mode %s" % mode_parameter)


def parse_color(color_parameter):

    if re.fullmatch("^[0-9a-f]{6}$", color_parameter):  # Color in HTML notation
        color = [int(color_parameter[i:i+2], 16) for i in [0, 2, 4]]
        return color
    else:
        raise LineParseError("%s is not a valid color" % color_parameter)


def parse_time_period(duration_parameter, current_period):
    new_period = current_period + duration_parameter

    if new_period > 0xFFFF:
        raise ConfigError("Time period %d is too large." % new_period)

    return new_period


def update_colors_map(colors_map, keycodes, keymode, color=None, effect_name=None, react_color=None, react_duration=None):

    # Modes:
    #       0: Effect, Manual Refresh
    #       1: Static
    #       2: Effect, Automatic Refresh

    for k in keycodes:
        colors_map[k] = KeyBlock()
        if keymode == "effect":
            colors_map[k].mode = 0
            colors_map[k].effect_name = effect_name
        elif keymode == "steady":
            colors_map[k].mode = 1
            colors_map[k].color = color
        elif keymode == "reactive":
            colors_map[k].mode = 8
            colors_map[k].color = color
            colors_map[k].react_color = react_color
            colors_map[k].react_duration = react_duration
        else:
            raise ConfigParseError("Invalid key mode detected for keycode %s" % k)

    return colors_map


def effect_add_transition(effect_map, name, color, duration):
    if len(effect_map[name].transition_list) > 16:
        raise ConfigParseError("There are too many transitions attached to effect %s. (read %d transitions)" % name, len(effect_map.transition_list))
    effect_map[name].transition_list.append(Transition(color, duration))

    return effect_map


def verify_effect(effect_map):
    # Currently, only check if the period is larger then FF.
    # TODO: Determine what else and how else effects can be verified.

    for key in effect_map:
        period = 0
        for trans in effect_map[key].transition_list:
            period += trans.duration
            if period > 0xFFFF:
                raise ConfigParseError("Total transition duration is too long. (length: %d ms)" % period)
        effect_map[key].period = period

    return effect_map


def verify_percentage(percent):
    if percent <= 100 | percent >= 100:
        return percent / 100
    else:
        raise ConfigParseError("Percentage value is invalid. (length: %d ms)" % percent)
