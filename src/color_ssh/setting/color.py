from __future__ import division, print_function, absolute_import, unicode_literals

# ANSI color definitions

RESET = b'\033[0m'

INVERSE = b'\033[7m'

BLACK = b'\033[30m'
RED = b'\033[31m'
GREEN = b'\033[32m'
BROWN = b'\033[33m'
BLUE = b'\033[34m'
MAGENTA = b'\033[35m'
CYAN = b'\033[36m'
GRAY = b'\033[37m'

DARK_GRAY = b'\033[90m'
LIGHT_RED = b'\033[91m'
LIGHT_GREEN = b'\033[92m'
LIGHT_BROWN = b'\033[93m'
LIGHT_BLUE = b'\033[94m'
LIGHT_MAGENTA = b'\033[95m'
LIGHT_CYAN = b'\033[96m'
WHITE = b'\033[97m'

COLOR_SET = [
    RED,
    GREEN,
    BROWN,
    BLUE,
    MAGENTA,
    CYAN,
    GRAY,
]

COLOR_NAMES = {
    'black': BLACK,
    'red': RED,
    'green': GREEN,
    'brown': BROWN,
    'yellow': BROWN,
    'blue': BLUE,
    'magenta': MAGENTA,
    'cyan': CYAN,
    'gray': GRAY,
    'white': WHITE,
}
