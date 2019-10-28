NB_KEYS = 42
REGION_ID_CODES = {"alphanum": 0x2a, "enter": 0x0b, "modifiers": 0x18, "numpad": 0x24}


def make_key_colors_packet(region, colors_map):

    packet = []

    region_hexcode = REGION_ID_CODES[region]
    header = [0x0e, 0x00, region_hexcode, 0x00]
    packet += header

    k = 0
    for keycode, rgb in colors_map.items():

        key_fragment = rgb + [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00] + [keycode]
        packet += key_fragment
        k += 1

    while k < NB_KEYS:

        packet += ([0x00] * 12)
        k += 1

    packet += [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x39]

    return packet


def make_refresh_packet():

    packet = [0x09] + [0x00] * 63

    return packet
