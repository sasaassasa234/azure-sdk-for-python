"""Renderer utilities for exporting maps to images."""

from __future__ import annotations

from typing import Dict, Tuple

from PIL import Image

from tiles import Tile


class MapRenderer:
    """Render a map array to a PNG image."""

    def __init__(self, tile_size: int = 6) -> None:
        """Initialize the renderer with a tile size."""

        self.tile_size = tile_size
        self.colors: Dict[Tile, Tuple[int, int, int]] = {
            Tile.WALL: (30, 30, 30),
            Tile.FLOOR: (200, 200, 200),
            Tile.DOOR: (160, 110, 60),
            Tile.START: (80, 200, 120),
            Tile.EXIT: (200, 70, 70),
        }

    def export_to_image(self, grid, output_path: str) -> None:
        """Export a grid of tiles to a PNG image."""

        height, width = grid.shape
        image = Image.new("RGB", (width * self.tile_size, height * self.tile_size))
        pixels = image.load()

        for y in range(height):
            for x in range(width):
                color = self.colors.get(grid[y, x], (0, 0, 0))
                self._fill_tile(pixels, x, y, color)

        image.save(output_path, format="PNG")

    def _fill_tile(self, pixels, tile_x: int, tile_y: int, color: Tuple[int, int, int]) -> None:
        """Fill the square pixels for a single tile."""

        start_x = tile_x * self.tile_size
        start_y = tile_y * self.tile_size
        for y in range(start_y, start_y + self.tile_size):
            for x in range(start_x, start_x + self.tile_size):
                pixels[x, y] = color
