#!/usr/bin/env python3
"""
Example 01: Avatar Generation

Generate a studio-quality avatar from a selfie and full-body posture image.
This is the first step in the virtual try-on pipeline.

Usage:
    python examples/01_avatar.py --selfie path/to/selfie.jpg --posture path/to/fullbody.jpg

Requirements:
    - GOOGLE_API_KEY environment variable (or use --mock for testing)
"""

import argparse
from pathlib import Path

from openvto import OpenVTO


def main():
    parser = argparse.ArgumentParser(description="Generate a studio avatar")
    parser.add_argument(
        "--selfie", type=str, required=True, help="Path to selfie image"
    )
    parser.add_argument(
        "--posture", type=str, required=True, help="Path to full-body image"
    )
    parser.add_argument(
        "--output", type=str, default="avatar_output.png", help="Output path"
    )
    parser.add_argument(
        "--background", type=str, default="studio", choices=["studio", "white"]
    )
    parser.add_argument(
        "--mock", action="store_true", help="Use mock provider for testing"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    args = parser.parse_args()

    # Validate inputs
    selfie_path = Path(args.selfie)
    posture_path = Path(args.posture)

    if not selfie_path.exists():
        print(f"Error: Selfie not found: {selfie_path}")
        return 1
    if not posture_path.exists():
        print(f"Error: Posture image not found: {posture_path}")
        return 1

    # Initialize client
    provider = "mock" if args.mock else "google"
    vto = OpenVTO(provider=provider)

    print(f"Generating avatar...")
    print(f"  Selfie: {selfie_path}")
    print(f"  Posture: {posture_path}")
    print(f"  Background: {args.background}")
    print(f"  Provider: {provider}")

    # Generate avatar
    result = vto.generate_avatar(
        selfie=str(selfie_path),
        posture=str(posture_path),
        background=args.background,
        seed=args.seed,
    )

    # Save output
    output_path = Path(args.output)
    output_path.write_bytes(result.image)

    print(f"\n✓ Avatar generated successfully!")
    print(f"  Output: {output_path}")
    print(f"  Size: {result.avatar.width}x{result.avatar.height}")
    print(f"  Latency: {result.meta.latency_ms:.0f}ms")
    print(f"  Cache hit: {result.meta.cache_hit}")
    print(f"  Model: {result.meta.model}")

    return 0


if __name__ == "__main__":
    exit(main())
