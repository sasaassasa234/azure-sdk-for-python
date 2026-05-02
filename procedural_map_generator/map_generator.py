"""Procedural room-and-corridor dungeon map generator."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import List, Optional, Sequence, Tuple

import numpy as np

from tiles import Tile


@dataclass
class Room:
    """Represents a rectangular room."""

    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Tuple[int, int]:
        """Return the center coordinate of the room."""

        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        return center_x, center_y

    def intersects(self, other: "Room", padding: int = 1) -> bool:
        """Return True if this room overlaps another room."""

        return (
            self.x - padding < other.x + other.width
            and self.x + self.width + padding > other.x
            and self.y - padding < other.y + other.height
            and self.y + self.height + padding > other.y
        )


class MapGenerator:
    """Generates a dungeon map with rooms, corridors, and special tiles."""

    def __init__(
        self,
        width: int = 100,
        height: int = 100,
        room_count_range: Tuple[int, int] = (12, 18),
        room_size_range: Tuple[int, int] = (6, 14),
        corridor_width: int = 1,
        seed: Optional[int] = None,
        cave_mode: bool = False,
    ) -> None:
        """Initialize the generator with configuration options."""

        self.width = width
        self.height = height
        self.room_count_range = room_count_range
        self.room_size_range = room_size_range
        self.corridor_width = corridor_width
        self.seed = seed
        self.cave_mode = cave_mode

        self.random = random.Random(seed)
        self.map = np.full((height, width), Tile.WALL, dtype=object)
        self.rooms: List[Room] = []

    def generate(self) -> np.ndarray:
        """Generate a full dungeon map."""

        if self.cave_mode:
            self._generate_cave()
        else:
            self.generate_rooms()
            self.connect_rooms()
        self.place_start_and_exit()
        return self.map

    def generate_rooms(self) -> None:
        """Generate non-overlapping rooms within the map."""

        target_room_count = self.random.randint(*self.room_count_range)
        attempts = target_room_count * 5

        while len(self.rooms) < target_room_count and attempts > 0:
            attempts -= 1
            width = self.random.randint(*self.room_size_range)
            height = self.random.randint(*self.room_size_range)
            x = self.random.randint(1, self.width - width - 2)
            y = self.random.randint(1, self.height - height - 2)
            new_room = Room(x, y, width, height)

            if any(new_room.intersects(existing) for existing in self.rooms):
                continue

            self.rooms.append(new_room)
            self._carve_room(new_room)

    def connect_rooms(self) -> None:
        """Connect rooms using L-shaped corridors to ensure reachability."""

        if not self.rooms:
            return

        sorted_rooms = sorted(self.rooms, key=lambda room: room.center)
        for index in range(1, len(sorted_rooms)):
            start = sorted_rooms[index - 1].center
            end = sorted_rooms[index].center
            self.carve_corridor(start, end)

        self._place_doors()

    def carve_corridor(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Carve an L-shaped corridor between two points."""

        x1, y1 = start
        x2, y2 = end
        if self.random.random() < 0.5:
            self._carve_horizontal(x1, x2, y1)
            self._carve_vertical(y1, y2, x2)
        else:
            self._carve_vertical(y1, y2, x1)
            self._carve_horizontal(x1, x2, y2)

    def place_start_and_exit(self) -> None:
        """Place start and exit tiles on floor positions."""

        floor_positions = list(zip(*np.where(self.map == Tile.FLOOR)))
        if len(floor_positions) < 2:
            return

        start = self.random.choice(floor_positions)
        exit_tile = max(
            floor_positions,
            key=lambda pos: self._distance(start, pos),
        )

        self.map[start] = Tile.START
        self.map[exit_tile] = Tile.EXIT

    def get_ascii_preview(self, max_width: int = 120) -> str:
        """Return an ASCII preview of the map."""

        scale = max(1, math.ceil(self.width / max_width))
        rows = []
        for y in range(0, self.height, scale):
            row_tiles = []
            for x in range(0, self.width, scale):
                row_tiles.append(self.map[y, x].name[0])
            rows.append("".join(row_tiles))
        return "\n".join(rows)

    def _carve_room(self, room: Room) -> None:
        """Carve out the tiles within a room."""

        self.map[room.y : room.y + room.height, room.x : room.x + room.width] = Tile.FLOOR

    def _carve_horizontal(self, x1: int, x2: int, y: int) -> None:
        """Carve a horizontal corridor segment."""

        start_x, end_x = sorted((x1, x2))
        for x in range(start_x, end_x + 1):
            self._carve_tile_block(x, y)

    def _carve_vertical(self, y1: int, y2: int, x: int) -> None:
        """Carve a vertical corridor segment."""

        start_y, end_y = sorted((y1, y2))
        for y in range(start_y, end_y + 1):
            self._carve_tile_block(x, y)

    def _carve_tile_block(self, x: int, y: int) -> None:
        """Carve a corridor tile with the configured corridor width."""

        half = self.corridor_width // 2
        for offset_x in range(-half, half + 1):
            for offset_y in range(-half, half + 1):
                carve_x = min(max(x + offset_x, 1), self.width - 2)
                carve_y = min(max(y + offset_y, 1), self.height - 2)
                self.map[carve_y, carve_x] = Tile.FLOOR

    def _place_doors(self) -> None:
        """Place doors on corridor-room transitions."""

        for room in self.rooms:
            for x in range(room.x, room.x + room.width):
                self._maybe_place_door(x, room.y - 1, x, room.y)
                self._maybe_place_door(x, room.y + room.height, x, room.y + room.height - 1)
            for y in range(room.y, room.y + room.height):
                self._maybe_place_door(room.x - 1, y, room.x, y)
                self._maybe_place_door(room.x + room.width, y, room.x + room.width - 1, y)

    def _maybe_place_door(
        self,
        wall_x: int,
        wall_y: int,
        room_x: int,
        room_y: int,
    ) -> None:
        """Replace a wall tile with a door if it connects to a corridor."""

        if not (0 <= wall_x < self.width and 0 <= wall_y < self.height):
            return

        if self.map[wall_y, wall_x] != Tile.FLOOR:
            return

        if self.map[room_y, room_x] == Tile.FLOOR and self.random.random() < 0.25:
            self.map[wall_y, wall_x] = Tile.DOOR

    def _generate_cave(self) -> None:
        """Generate a simple noise-based cave layout."""

        noise = self.random.random
        for y in range(self.height):
            for x in range(self.width):
                if noise() > 0.45:
                    self.map[y, x] = Tile.FLOOR

        for _ in range(4):
            self.map = self._smooth_map(self.map)

        self.rooms = []

    def _smooth_map(self, grid: np.ndarray) -> np.ndarray:
        """Apply cellular automata smoothing to the map."""

        new_grid = grid.copy()
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                neighbors = self._count_floor_neighbors(grid, x, y)
                if neighbors >= 5:
                    new_grid[y, x] = Tile.FLOOR
                else:
                    new_grid[y, x] = Tile.WALL
        return new_grid

    def _count_floor_neighbors(self, grid: np.ndarray, x: int, y: int) -> int:
        """Count floor tiles around a position."""

        count = 0
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                if grid[y + offset_y, x + offset_x] == Tile.FLOOR:
                    count += 1
        return count

    def _distance(self, start: Sequence[int], end: Sequence[int]) -> float:
        """Return Euclidean distance between two positions."""

        return math.hypot(end[0] - start[0], end[1] - start[1])
