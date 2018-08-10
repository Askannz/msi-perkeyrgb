import ctypes as ct

# Courtesy of https://github.com/apmorton/pyhidapi/issues/16


def set_hidapi_types(hidapi):

    hidapi.hid_init.argtypes = []
    hidapi.hid_init.restype = ct.c_int
    hidapi.hid_exit.argtypes = []
    hidapi.hid_exit.restype = ct.c_int
    hidapi.hid_enumerate.argtypes = [ct.c_ushort, ct.c_ushort]
    # hidapi.hid_enumerate.restype = ct.POINTER(DeviceInfo)
    # hidapi.hid_free_enumeration.argtypes = [ct.POINTER(DeviceInfo)]
    hidapi.hid_free_enumeration.restype = None
    hidapi.hid_open.argtypes = [ct.c_ushort, ct.c_ushort, ct.c_wchar_p]
    hidapi.hid_open.restype = ct.c_void_p
    hidapi.hid_open_path.argtypes = [ct.c_char_p]
    hidapi.hid_open_path.restype = ct.c_void_p
    hidapi.hid_write.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_size_t]
    hidapi.hid_write.restype = ct.c_int
    hidapi.hid_read_timeout.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_size_t, ct.c_int]
    hidapi.hid_read_timeout.restype = ct.c_int
    hidapi.hid_read.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_size_t]
    hidapi.hid_read.restype = ct.c_int
    hidapi.hid_set_nonblocking.argtypes = [ct.c_void_p, ct.c_int]
    hidapi.hid_set_nonblocking.restype = ct.c_int
    hidapi.hid_send_feature_report.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_int]
    hidapi.hid_send_feature_report.restype = ct.c_int
    hidapi.hid_get_feature_report.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_size_t]
    hidapi.hid_get_feature_report.restype = ct.c_int
    hidapi.hid_close.argtypes = [ct.c_void_p]
    hidapi.hid_close.restype = None
    hidapi.hid_get_manufacturer_string.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_size_t]
    hidapi.hid_get_manufacturer_string.restype = ct.c_int
    hidapi.hid_get_product_string.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_size_t]
    hidapi.hid_get_product_string.restype = ct.c_int
    hidapi.hid_get_serial_number_string.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_size_t]
    hidapi.hid_get_serial_number_string = ct.c_int
    hidapi.hid_get_indexed_string.argtypes = [ct.c_void_p, ct.c_int, ct.c_wchar_p, ct.c_size_t]
    hidapi.hid_get_indexed_string.restype = ct.c_int
    hidapi.hid_error.argtypes = [ct.c_void_p]
    hidapi.hid_error.restype = ct.c_wchar_p
