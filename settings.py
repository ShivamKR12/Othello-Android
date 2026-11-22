import os
import sys

# Game Constants
FPS = 30
SPACESIZE = 50
BOARDWIDTH = 8
BOARDHEIGHT = 8

# Tile Constants
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 50, 255)
BROWN = (174, 94, 0)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller / Buildozer packages."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "assets", relative_path)
