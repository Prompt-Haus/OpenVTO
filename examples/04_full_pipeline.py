#!/usr/bin/env python3
"""
Example 04: Full Pipeline

Run the complete OpenVTO pipeline: avatar → try-on → video loop.
This is the most common use case for generating a complete virtual try-on.

Usage:
    python examples/04_full_pipeline.py \\
        --selfie selfie.jpg \\
        --posture fullbody.jpg \\
        --clothes shirt.jpg pants.jpg

Requirements:
    - GOOGLE_API_KEY environment variable (or use --mock for testing)
"""

import argparse
from pathlib import Path

from openvto import OpenVTO, ClothingItem


def main():
    parser = argparse.ArgumentParser(description="Run full virtual try-on pipeline")
    parser.add_argument("--selfie", type=str, required=True, help="Path to selfie")
    parser.add_argument("--posture", type=str, required=True, help="Path to full-body image")
    parser.add_argument("--clothes", type=str, nargs="+", required=True, help="Clothing images")
    parser.add_argument("--output-dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--no-video", action="store_true", help="Skip video generation")
    parser.add_argument("--mock", action="store_true", help="Use mock provider for testing")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    # Validate inputs
    selfie_path = Path(args.selfie)
    posture_path = Path(args.posture)

    if not selfie_path.exists():
        print(f"Error: Selfie not found: {selfie_path}")
        return 1
    if not posture_path.exists():
        print(f"Error: Posture not found: {posture_path}")
        return 1

    clothing_paths = []
    for c in args.clothes:
        p = Path(c)
        if not p.exists():
            print(f"Error: Clothing not found: {p}")
            return 1
        clothing_paths.append(p)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize client
    provider = "mock" if args.mock else "google"
    vto = OpenVTO(provider=provider)

    print("=" * 50)
    print("OpenVTO Full Pipeline")
    print("=" * 50)
    print(f"Selfie: {selfie_path}")
    print(f"Posture: {posture_path}")
    print(f"Clothing: {len(clothing_paths)} item(s)")
    print(f"Video: {'No' if args.no_video else 'Yes'}")
    print(f"Provider: {provider}")
    print("=" * 50)

    # Create clothing items
    items = [
        ClothingItem(id=f"item_{i}", image=str(p), name=p.stem)
        for i, p in enumerate(clothing_paths)
    ]

    # Run full pipeline
    print("\n⏳ Running pipeline...")
    result = vto.pipeline(
        selfie=str(selfie_path),
        posture=str(posture_path),
        clothes=items,
        make_video=not args.no_video,
        seed=args.seed,
    )

    # Save avatar
    avatar_path = output_dir / "01_avatar.png"
    avatar_path.write_bytes(result.avatar.image)
    print(f"  ✓ Avatar saved: {avatar_path}")

    # Save try-on
    tryon_path = output_dir / "02_tryon.png"
    tryon_path.write_bytes(result.tryon.image)
    print(f"  ✓ Try-on saved: {tryon_path}")

    # Save video if generated
    if result.has_video:
        video_path = output_dir / "03_video.mp4"
        video_path.write_bytes(result.video.video)
        print(f"  ✓ Video saved: {video_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("Pipeline Complete!")
    print("=" * 50)
    print(f"Total time: {result.total_latency_ms:.0f}ms ({result.total_latency_ms/1000:.1f}s)")
    print(f"\nStep breakdown:")
    print(f"  Avatar: {result.avatar.meta.latency_ms:.0f}ms")
    print(f"  Try-on: {result.tryon.meta.latency_ms:.0f}ms")
    if result.has_video:
        print(f"  Video:  {result.video.meta.latency_ms:.0f}ms")
    print(f"\nOutputs saved to: {output_dir.absolute()}")

    return 0


if __name__ == "__main__":
    exit(main())

