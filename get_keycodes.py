import sys

HEADER_LEN = 4
KEY_SETUP_LEN = 12
NB_KEYS = 42


filepath = sys.argv[1]

f = open(filepath, "r")

data = f.readline()

hexcodes = [data[i:i+2] for i in range(0, len(data), 2)]

array_str = "["
index = HEADER_LEN

# Key setup
for k in range(NB_KEYS):

    key_setup_hexcodes = hexcodes[index:index+KEY_SETUP_LEN]

    array_str += ("0x" + key_setup_hexcodes[-1])

    if k != NB_KEYS - 1:
        array_str += ', '

    index += KEY_SETUP_LEN

array_str += "]"

print(array_str)
