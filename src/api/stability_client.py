"""Stability AI (Stable Diffusion 3) image generation client."""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path

from .base import ImageAPIClient, GenerationResult


class StabilityClient(ImageAPIClient):
    """Client for Stability AI Stable Diffusion 3 image generation."""

    API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("STABILITY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Stability API key is required. Set STABILITY_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate(self, prompt: str, output_path: str, size: str = "1024x1024") -> GenerationResult:
        # Stability AI uses multipart/form-data
        boundary = "----PosterSkillBoundary"
        aspect_ratio = self._size_to_aspect(size)

        fields = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": "png",
            "model": "sd3-large",
        }

        body = b""
        for key, value in fields.items():
            body += f"--{boundary}\r\n".encode()
            body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode()
            body += f"{value}\r\n".encode()
        body += f"--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            self.API_URL,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                image_bytes = resp.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise RuntimeError(f"Stability API error {e.code}: {error_body}") from e

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return GenerationResult(
            image_path=output_path,
            prompt_used=prompt,
            provider="stability",
            model="sd3-large",
        )

    @staticmethod
    def _size_to_aspect(size: str) -> str:
        w, h = size.split("x")
        w, h = int(w), int(h)
        if w == h:
            return "1:1"
        elif w > h:
            return "16:9"
        else:
            return "9:16"
