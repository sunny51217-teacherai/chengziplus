#!/usr/bin/env python3
"""Teaching Poster Generator - Main entry point.

Generates educational posters by combining pedagogical prompt engineering
with image generation APIs (DALL-E 3 / Stability AI / Silicon Flow).

Usage:
    python3 generate_poster.py --topic "光合作用" --grade "初中" --style vibrant --api openai
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env file if it exists
def load_dotenv(env_path: str) -> None:
    """Load environment variables from a .env file."""
    path = Path(env_path)
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                os.environ.setdefault(key, value)


def main():
    parser = argparse.ArgumentParser(
        description="Generate teaching posters using image generation APIs."
    )
    parser.add_argument(
        "--topic", required=True,
        help="Teaching topic, e.g. '光合作用 Photosynthesis'"
    )
    parser.add_argument(
        "--grade", default="初中",
        help="Target grade/audience (小学/初中/高中/大学 or English). Default: 初中"
    )
    parser.add_argument(
        "--style", default="vibrant",
        choices=["cartoon", "minimal", "academic", "vibrant"],
        help="Visual style for the poster. Default: vibrant"
    )
    parser.add_argument(
        "--api", default="openai",
        choices=["openai", "stability", "siliconflow"],
        help="Image generation API provider. Default: openai"
    )
    parser.add_argument(
        "--size", default="1024x1024",
        help="Image size (e.g. 1024x1024, 1024x1792). Default: 1024x1024"
    )
    parser.add_argument(
        "--output", default="./output",
        help="Output directory. Default: ./output"
    )
    parser.add_argument(
        "--env-file", default=None,
        help="Path to .env file. Default: auto-detect from project root"
    )

    args = parser.parse_args()

    # Load environment variables
    project_root = Path(__file__).resolve().parent.parent
    env_file = args.env_file or str(project_root / ".env")
    load_dotenv(env_file)

    # Import after env is loaded
    from prompts.poster_prompt import build_poster_prompt
    from api.factory import create_client

    # Build the prompt
    prompt = build_poster_prompt(args.topic, args.grade, args.style)
    print(f"[Poster] Topic: {args.topic}")
    print(f"[Poster] Grade: {args.grade}")
    print(f"[Poster] Style: {args.style}")
    print(f"[Poster] API: {args.api}")
    print(f"[Poster] Size: {args.size}")
    print(f"[Poster] Prompt:\n  {prompt}")
    print()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = args.topic.replace(" ", "_")[:30]
    filename = f"poster_{safe_topic}_{args.style}_{timestamp}.png"
    output_path = str(Path(args.output) / filename)

    # Create client and generate
    try:
        client = create_client(args.api)
    except ValueError as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[Poster] Generating image via {args.api}...")
    try:
        result = client.generate(prompt, output_path, size=args.size)
    except RuntimeError as e:
        print(f"[Error] API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[Poster] Image saved to: {result.image_path}")
    print(f"[Poster] Provider: {result.provider} / Model: {result.model}")
    if result.revised_prompt:
        print(f"[Poster] Revised prompt: {result.revised_prompt}")
    print("[Poster] Done!")


if __name__ == "__main__":
    main()
