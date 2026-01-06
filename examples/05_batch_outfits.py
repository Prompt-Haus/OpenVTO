#!/usr/bin/env python3
"""
Example 05: Batch Outfit Processing

Process multiple outfits on a single avatar efficiently.
Useful for catalog/e-commerce workflows where you want to show
the same model in different outfits.

Usage:
    python examples/05_batch_outfits.py \\
        --avatar avatar.png \\
        --outfits outfit1/shirt.jpg,outfit1/pants.jpg outfit2/dress.jpg

Requirements:
    - GOOGLE_API_KEY environment variable (or use --mock for testing)
"""

import argparse
from pathlib import Path

from openvto import OpenVTO, ClothingItem, Outfit


def parse_outfit(outfit_str: str) -> list[Path]:
    """Parse comma-separated outfit items."""
    return [Path(p.strip()) for p in outfit_str.split(",")]


def main():
    parser = argparse.ArgumentParser(description="Process multiple outfits")
    parser.add_argument(
        "--avatar", type=str, required=True, help="Path to avatar image"
    )
    parser.add_argument(
        "--outfits",
        type=str,
        nargs="+",
        required=True,
        help="Outfit specs (comma-separated items per outfit)",
    )
    parser.add_argument(
        "--output-dir", type=str, default="./batch_output", help="Output dir"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock provider")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    # Validate avatar
    avatar_path = Path(args.avatar)
    if not avatar_path.exists():
        print(f"Error: Avatar not found: {avatar_path}")
        return 1

    # Parse and validate outfits
    outfits = []
    for i, outfit_str in enumerate(args.outfits, 1):
        paths = parse_outfit(outfit_str)
        items = []
        for j, p in enumerate(paths):
            if not p.exists():
                print(f"Error: Clothing not found: {p}")
                return 1
            items.append(
                ClothingItem(id=f"outfit{i}_item{j}", image=str(p), name=p.stem)
            )
        outfits.append(Outfit(items=items, name=f"Outfit {i}"))

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize client
    provider = "mock" if args.mock else "google"
    vto = OpenVTO(provider=provider)

    print("=" * 50)
    print("OpenVTO Batch Processing")
    print("=" * 50)
    print(f"Avatar: {avatar_path}")
    print(f"Outfits: {len(outfits)}")
    for outfit in outfits:
        print(f"  - {outfit.name}: {len(outfit.items)} item(s)")
    print(f"Provider: {provider}")
    print("=" * 50)

    # Process each outfit
    results = []
    total_time = 0

    for i, outfit in enumerate(outfits, 1):
        print(f"\n⏳ Processing {outfit.name}...")

        result = vto.generate_tryon(
            avatar=str(avatar_path),
            clothes=outfit,
            seed=args.seed,
        )

        results.append(result)
        total_time += result.meta.latency_ms

        # Save output
        output_path = output_dir / f"outfit_{i:02d}.png"
        output_path.write_bytes(result.image)
        print(f"  ✓ Saved: {output_path} ({result.meta.latency_ms:.0f}ms)")

    # Print summary
    print("\n" + "=" * 50)
    print("Batch Complete!")
    print("=" * 50)
    print(f"Processed: {len(outfits)} outfits")
    print(f"Total time: {total_time:.0f}ms ({total_time/1000:.1f}s)")
    print(f"Average: {total_time/len(outfits):.0f}ms per outfit")
    print(f"\nOutputs saved to: {output_dir.absolute()}")

    # Show cache stats
    cache_hits = sum(1 for r in results if r.meta.cache_hit)
    if cache_hits > 0:
        print(f"Cache hits: {cache_hits}/{len(results)}")

    return 0


if __name__ == "__main__":
    exit(main())
