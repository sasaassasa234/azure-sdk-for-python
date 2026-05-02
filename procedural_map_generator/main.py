"""Entry point for the procedural map generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from map_generator import MapGenerator
from renderer import MapRenderer


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Procedural dungeon map generator.")
    parser.add_argument("--width", type=int, default=100, help="Map width in tiles.")
    parser.add_argument("--height", type=int, default=100, help="Map height in tiles.")
    parser.add_argument(
        "--room-count",
        nargs=2,
        type=int,
        default=(12, 18),
        metavar=("MIN", "MAX"),
        help="Room count range.",
    )
    parser.add_argument(
        "--room-size",
        nargs=2,
        type=int,
        default=(6, 14),
        metavar=("MIN", "MAX"),
        help="Room size range.",
    )
    parser.add_argument(
        "--corridor-width",
        type=int,
        default=1,
        help="Corridor width in tiles.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument(
        "--tile-size",
        type=int,
        default=6,
        help="Tile size in pixels for the rendered image.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated_map.png"),
        help="Output PNG file path.",
    )
    parser.add_argument(
        "--cave-mode",
        action="store_true",
        help="Generate a noise-based cave layout instead of rooms.",
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Print an ASCII preview to the console.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the map generator with CLI options."""

    args = parse_args()
    generator = MapGenerator(
        width=args.width,
        height=args.height,
        room_count_range=tuple(args.room_count),
        room_size_range=tuple(args.room_size),
        corridor_width=args.corridor_width,
        seed=args.seed,
        cave_mode=args.cave_mode,
    )
    grid = generator.generate()

    if args.ascii:
        print(generator.get_ascii_preview())

    renderer = MapRenderer(tile_size=args.tile_size)
    renderer.export_to_image(grid, str(args.output))
    print(f"Map saved to {args.output}")


if __name__ == "__main__":
    main()
