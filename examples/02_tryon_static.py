#!/usr/bin/env python3
"""
Example 02: Static Try-On

Generate a virtual try-on by placing clothing on an avatar image.
Can use either a pre-generated avatar or any full-body image.

Usage:
    python examples/02_tryon_static.py --avatar avatar.png --clothes shirt.jpg pants.jpg

Requirements:
    - GOOGLE_API_KEY environment variable (or use --mock for testing)
"""

import argparse
from pathlib import Path

from openvto import OpenVTO, ClothingItem, Outfit


def main():
    parser = argparse.ArgumentParser(description="Generate static try-on")
    parser.add_argument(
        "--avatar", type=str, required=True, help="Path to avatar/base image"
    )
    parser.add_argument(
        "--clothes", type=str, nargs="+", required=True, help="Clothing image(s)"
    )
    parser.add_argument(
        "--output", type=str, default="tryon_output.png", help="Output path"
    )
    parser.add_argument(
        "--mock", action="store_true", help="Use mock provider for testing"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--no-compose", action="store_true", help="Don't composite clothing"
    )
    args = parser.parse_args()

    # Validate inputs
    avatar_path = Path(args.avatar)
    if not avatar_path.exists():
        print(f"Error: Avatar not found: {avatar_path}")
        return 1

    clothing_paths = []
    for c in args.clothes:
        p = Path(c)
        if not p.exists():
            print(f"Error: Clothing image not found: {p}")
            return 1
        clothing_paths.append(p)

    # Initialize client
    provider = "mock" if args.mock else "google"
    vto = OpenVTO(provider=provider)

    print(f"Generating try-on...")
    print(f"  Avatar: {avatar_path}")
    print(f"  Clothing items: {len(clothing_paths)}")
    for i, p in enumerate(clothing_paths, 1):
        print(f"    {i}. {p}")
    print(f"  Provider: {provider}")

    # Create clothing items (can add descriptions for better results)
    items = [
        ClothingItem(id=f"item_{i}", image=str(p), name=p.stem)
        for i, p in enumerate(clothing_paths)
    ]

    # Generate try-on
    result = vto.generate_tryon(
        avatar=str(avatar_path),
        clothes=items,
        compose=not args.no_compose,
        seed=args.seed,
    )

    # Save output
    output_path = Path(args.output)
    output_path.write_bytes(result.image)

    print(f"\n✓ Try-on generated successfully!")
    print(f"  Output: {output_path}")
    print(f"  Latency: {result.meta.latency_ms:.0f}ms")
    print(f"  Cache hit: {result.meta.cache_hit}")
    print(f"  Model: {result.meta.model}")

    return 0


if __name__ == "__main__":
    exit(main())
