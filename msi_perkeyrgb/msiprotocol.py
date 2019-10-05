NB_KEYS = 42
REGION_ID_CODES = {"alphanum": 0x2a, "enter": 0x0b, "modifiers": 0x18, "numpad": 0x24}


def make_key_colors_packet(region, colors_map, effect_map):

    packet = []

    region_hexcode = REGION_ID_CODES[region]
    header = [0x0e, 0x00, region_hexcode, 0x00]
    packet += header

    k = 0
    for keycode, blkobj in colors_map.items():

        if blkobj.mode == 1:
            effect_id = effect_map[blkobj.effect_name].identifier
        else:
            effect_id = 0

        key_fragment = blkobj.color + [0x00, 0x00, 0x00, 0x00, 0x00] + [effect_id] + [blkobj.mode] + [0x00] + [keycode]
        packet += key_fragment
        k += 1

    while k < NB_KEYS:

        packet += ([0x00] * 12)
        k += 1

    packet += [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x39]

    return packet


def make_effect_packet(effect_entry):
    packet = []
    header = [0xb0, 0x00]
    packet += header

    # begin transition blocks
    x = 0
    for transition in effect_entry.transition_list:
        if x == 0:
            packet += bytearray(effect_entry.identifier)
        else:
            packet += bytearray(x)

    return packet


def make_refresh_packet():

    packet = [0x09] + [0x00] * 63

    return packet
