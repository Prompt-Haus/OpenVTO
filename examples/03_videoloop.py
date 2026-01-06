#!/usr/bin/env python3
"""
Example 03: Video Loop Generation

Generate an animated video loop from a static try-on image.
Supports different animation modes: 360° turn or idle breathing.

Usage:
    python examples/03_videoloop.py --image tryon.png --mode 360

Requirements:
    - GOOGLE_API_KEY environment variable (or use --mock for testing)
"""

import argparse
from pathlib import Path

from openvto import OpenVTO


def main():
    parser = argparse.ArgumentParser(description="Generate video loop")
    parser.add_argument("--image", type=str, required=True, help="Path to static image")
    parser.add_argument("--output", type=str, default="videoloop_output.mp4", help="Output path")
    parser.add_argument("--mode", type=str, default="360", choices=["360", "idle"])
    parser.add_argument("--seconds", type=float, default=4.0, help="Duration (4-8 seconds)")
    parser.add_argument("--mock", action="store_true", help="Use mock provider for testing")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    # Validate inputs
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        return 1

    if args.seconds < 4 or args.seconds > 8:
        print(f"Error: Duration must be between 4-8 seconds")
        return 1

    # Initialize client
    provider = "mock" if args.mock else "google"
    vto = OpenVTO(provider=provider)

    mode_desc = "360° rotation" if args.mode == "360" else "idle/breathing"
    print(f"Generating video loop...")
    print(f"  Image: {image_path}")
    print(f"  Mode: {mode_desc}")
    print(f"  Duration: {args.seconds}s")
    print(f"  Provider: {provider}")

    # Generate video loop
    result = vto.generate_videoloop(
        static_image=str(image_path),
        mode=args.mode,
        seconds=args.seconds,
        seed=args.seed,
    )

    # Save outputs
    output_path = Path(args.output)
    output_path.write_bytes(result.video)

    # Also save first frame
    first_frame_path = output_path.with_suffix(".first_frame.png")
    first_frame_path.write_bytes(result.first_frame)

    print(f"\n✓ Video loop generated successfully!")
    print(f"  Video: {output_path}")
    print(f"  First frame: {first_frame_path}")
    print(f"  Duration: {result.duration_seconds}s")
    print(f"  Size: {result.width}x{result.height}")
    print(f"  Latency: {result.meta.latency_ms:.0f}ms")
    print(f"  Cache hit: {result.meta.cache_hit}")
    print(f"  Model: {result.meta.model}")

    return 0


if __name__ == "__main__":
    exit(main())

