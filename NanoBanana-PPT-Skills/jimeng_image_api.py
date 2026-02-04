"""
Jimeng AI (即梦) Image & Video Generation API Client.

Uses the Volcengine Ark API to generate images via doubao-seedream
and videos via doubao-seedance models.
"""

import os
import sys
import time
import requests
from pathlib import Path
from typing import Optional


# =============================================================================
# Constants
# =============================================================================

ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# Image generation
IMAGE_MODEL = "doubao-seedream-4-0-250828"
IMAGE_ENDPOINT = f"{ARK_BASE_URL}/images/generations"

# Video generation (text-to-video)
VIDEO_T2V_MODEL = "doubao-seedance-1-0-lite-t2v-250428"
# Video generation (image-to-video)
VIDEO_I2V_MODEL = "doubao-seedance-1-0-lite-i2v-250428"
VIDEO_ENDPOINT = f"{ARK_BASE_URL}/contents/generations/tasks"

# Size mapping for 16:9 aspect ratio
SIZE_MAP = {
    "2K": "1792x1024",
    "4K": "1792x1024",  # Seedream max is 1792x1024, upscale if needed
}

# Video polling
VIDEO_POLL_INTERVAL = 5  # seconds
VIDEO_MAX_WAIT = 300  # 5 minutes max


# =============================================================================
# Authentication
# =============================================================================

def get_api_key() -> str:
    """Get the ARK_API_KEY from environment."""
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key or api_key == "your-ark-api-key-here":
        print("Error: ARK_API_KEY environment variable not set")
        print("Please set your Volcengine Ark API key in .env file")
        print("Get one at: https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey")
        sys.exit(1)
    return api_key


def _headers(api_key: str) -> dict:
    """Build request headers."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


# =============================================================================
# Image Generation
# =============================================================================

def generate_image(
    prompt: str,
    output_path: str,
    resolution: str = "2K",
) -> Optional[str]:
    """
    Generate an image using Jimeng Seedream model.

    Args:
        prompt: Text prompt for image generation.
        output_path: Full path to save the generated image.
        resolution: Image resolution key (2K or 4K).

    Returns:
        Path to saved image, or None if generation failed.
    """
    api_key = get_api_key()
    size = SIZE_MAP.get(resolution, SIZE_MAP["2K"])

    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "url",
    }

    try:
        resp = requests.post(
            IMAGE_ENDPOINT,
            json=payload,
            headers=_headers(api_key),
            timeout=120,
        )

        if resp.status_code != 200:
            error_detail = resp.text[:500]
            print(f"  Jimeng API error ({resp.status_code}): {error_detail}")
            return None

        data = resp.json()
        image_url = data["data"][0]["url"]

        # Download image
        img_resp = requests.get(image_url, timeout=60)
        if img_resp.status_code != 200:
            print(f"  Failed to download image from URL")
            return None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_resp.content)

        return output_path

    except Exception as e:
        print(f"  Jimeng image generation failed: {e}")
        return None


# =============================================================================
# Video Generation (Text-to-Video)
# =============================================================================

def generate_video_from_text(
    prompt: str,
    output_path: str,
    duration: int = 5,
    resolution: str = "720p",
) -> Optional[str]:
    """
    Generate a video from text using Jimeng Seedance model.

    Args:
        prompt: Text prompt for video generation.
        output_path: Full path to save the generated video.
        duration: Video duration in seconds (5 or 10).
        resolution: Video resolution (480p, 720p, 1080p).

    Returns:
        Path to saved video, or None if generation failed.
    """
    api_key = get_api_key()

    payload = {
        "model": VIDEO_T2V_MODEL,
        "content": [
            {
                "type": "text",
                "text": f"{prompt} --resolution {resolution} --duration {duration}",
            }
        ],
    }

    try:
        # Submit task
        resp = requests.post(
            VIDEO_ENDPOINT,
            json=payload,
            headers=_headers(api_key),
            timeout=30,
        )

        if resp.status_code != 200:
            error_detail = resp.text[:500]
            print(f"  Jimeng video API error ({resp.status_code}): {error_detail}")
            return None

        task_data = resp.json()
        task_id = task_data["id"]
        print(f"  Video task submitted: {task_id}")

        # Poll for results
        elapsed = 0
        while elapsed < VIDEO_MAX_WAIT:
            time.sleep(VIDEO_POLL_INTERVAL)
            elapsed += VIDEO_POLL_INTERVAL

            status_resp = requests.get(
                f"{VIDEO_ENDPOINT}/{task_id}",
                headers=_headers(api_key),
                timeout=30,
            )

            if status_resp.status_code != 200:
                print(f"  Poll error ({status_resp.status_code})")
                continue

            result = status_resp.json()
            status = result.get("status", "")

            if status == "succeeded":
                video_url = result["content"]["video_url"]
                # Download video
                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code != 200:
                    print(f"  Failed to download video")
                    return None

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(vid_resp.content)
                return output_path

            elif status == "failed":
                error = result.get("error", {})
                print(f"  Video generation failed: {error}")
                return None

            print(f"  Video generating... ({elapsed}s)")

        print(f"  Video generation timed out after {VIDEO_MAX_WAIT}s")
        return None

    except Exception as e:
        print(f"  Jimeng video generation failed: {e}")
        return None


# =============================================================================
# Video Generation (Image-to-Video)
# =============================================================================

def generate_video_from_image(
    image_path: str,
    prompt: str,
    output_path: str,
    duration: int = 5,
    resolution: str = "720p",
) -> Optional[str]:
    """
    Generate a video from a reference image using Jimeng Seedance model.

    Args:
        image_path: Path to the source image file.
        prompt: Text prompt describing the desired motion/video.
        output_path: Full path to save the generated video.
        duration: Video duration in seconds.
        resolution: Video resolution.

    Returns:
        Path to saved video, or None if generation failed.
    """
    import base64

    api_key = get_api_key()

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = Path(image_path).suffix.lstrip(".")
    mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    payload = {
        "model": VIDEO_I2V_MODEL,
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{image_data}",
                },
            },
            {
                "type": "text",
                "text": f"{prompt} --resolution {resolution} --duration {duration}",
            },
        ],
    }

    try:
        resp = requests.post(
            VIDEO_ENDPOINT,
            json=payload,
            headers=_headers(api_key),
            timeout=60,
        )

        if resp.status_code != 200:
            error_detail = resp.text[:500]
            print(f"  Jimeng i2v API error ({resp.status_code}): {error_detail}")
            return None

        task_data = resp.json()
        task_id = task_data["id"]
        print(f"  I2V task submitted: {task_id}")

        # Poll for results (same logic as t2v)
        elapsed = 0
        while elapsed < VIDEO_MAX_WAIT:
            time.sleep(VIDEO_POLL_INTERVAL)
            elapsed += VIDEO_POLL_INTERVAL

            status_resp = requests.get(
                f"{VIDEO_ENDPOINT}/{task_id}",
                headers=_headers(api_key),
                timeout=30,
            )

            if status_resp.status_code != 200:
                continue

            result = status_resp.json()
            status = result.get("status", "")

            if status == "succeeded":
                video_url = result["content"]["video_url"]
                vid_resp = requests.get(video_url, timeout=120)
                if vid_resp.status_code != 200:
                    print(f"  Failed to download video")
                    return None

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(vid_resp.content)
                return output_path

            elif status == "failed":
                error = result.get("error", {})
                print(f"  I2V generation failed: {error}")
                return None

            print(f"  I2V generating... ({elapsed}s)")

        print(f"  I2V generation timed out after {VIDEO_MAX_WAIT}s")
        return None

    except Exception as e:
        print(f"  Jimeng I2V generation failed: {e}")
        return None
