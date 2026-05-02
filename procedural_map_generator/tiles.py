"""Tile definitions for the procedural map generator."""

from enum import Enum


class Tile(Enum):
    """Enumeration of tile types used in the map."""

    WALL = 0
    FLOOR = 1
    DOOR = 2
    START = 3
    EXIT = 4


TILE_GLYPHS = {
    Tile.WALL: "#",
    Tile.FLOOR: ".",
    Tile.DOOR: "+",
    Tile.START: "S",
    Tile.EXIT: "E",
}

# Legend for colors used in renderer.py:
# WALL  -> dark gray
# FLOOR -> light gray
# DOOR  -> brown
# START -> green
# EXIT  -> red
