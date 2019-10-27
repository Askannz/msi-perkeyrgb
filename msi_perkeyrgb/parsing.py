import re
from .protocol_data.msi_keymaps import AVAILABLE_MSI_KEYMAPS


class UnknownModelError(Exception):
    pass


class UnknownIdError(Exception):
    pass


class UnknownPresetError(Exception):
    pass


def parse_model(model_arg):

    model_arg_nocase = model_arg.upper()
    for msi_models, _ in AVAILABLE_MSI_KEYMAPS:
        for model in msi_models:
            if model == model_arg_nocase:
                return model
    else:
        raise UnknownModelError(model_arg)


def parse_usb_id(id_arg):

    if re.fullmatch("^[0-9a-f]{4}:[0-9a-f]{4}$", id_arg):
        vid, pid = [int(s, 16) for s in id_arg.split(':')]
        return (vid, pid)
    else:
        raise UnknownIdError(id_arg)


def parse_preset(preset_arg, msi_presets):

    if preset_arg in msi_presets.keys():
        return preset_arg
    else:
        raise UnknownPresetError(preset_arg)
