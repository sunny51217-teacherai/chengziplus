"""OpenAI DALL-E 3 image generation client."""

import os
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

from .base import ImageAPIClient, GenerationResult


class OpenAIClient(ImageAPIClient):
    """Client for OpenAI DALL-E 3 image generation."""

    API_URL = "https://api.openai.com/v1/images/generations"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate(self, prompt: str, output_path: str, size: str = "1024x1024") -> GenerationResult:
        payload = json.dumps({
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }).encode("utf-8")

        req = urllib.request.Request(
            self.API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise RuntimeError(f"OpenAI API error {e.code}: {error_body}") from e

        image_data = body["data"][0]
        revised_prompt = image_data.get("revised_prompt")
        b64 = image_data["b64_json"]

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(b64))

        return GenerationResult(
            image_path=output_path,
            prompt_used=prompt,
            provider="openai",
            model="dall-e-3",
            revised_prompt=revised_prompt,
        )
