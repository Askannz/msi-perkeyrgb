import sys

HEADER_LEN = 4
KEY_SETUP_LEN = 12
NB_KEYS = 42
KECODE_LEN = 0
RGB_POS = 3


class bcolors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


filepath = sys.argv[1]

f = open(filepath, "r")

data = f.readline()

hexcodes = [data[i:i+2] for i in range(0, len(data), 2)]

index = 0

# Header
header_hexcodes = hexcodes[index:index+HEADER_LEN]
s = ' '.join(header_hexcodes) + '\n'
print('\n' + bcolors.GREEN + s + bcolors.ENDC)
index += HEADER_LEN

# Key setup
for k in range(NB_KEYS):

    key_setup_hexcodes = hexcodes[index:index+KEY_SETUP_LEN]

    rgb_hexcodes = key_setup_hexcodes[:3]
    middle_hexcodes = key_setup_hexcodes[3:-1]
    key_hexcodes = key_setup_hexcodes[-1:]

    s1 = ' '.join(rgb_hexcodes)
    s2 = ' '.join(middle_hexcodes)
    s3 = ' '.join(key_hexcodes)

    print(bcolors.RED + s1 + ' ' + bcolors.ENDC + s2 + ' ' + bcolors.GREEN + s3 + bcolors.ENDC)

    index += KEY_SETUP_LEN

end_hexcodes = hexcodes[index:]
s = '\n' + ' '.join(end_hexcodes)
print(bcolors.GREEN + s + bcolors.ENDC)
