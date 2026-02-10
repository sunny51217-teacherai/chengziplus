"""Silicon Flow (Flux) image generation client."""

import os
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

from .base import ImageAPIClient, GenerationResult


class SiliconFlowClient(ImageAPIClient):
    """Client for Silicon Flow Flux image generation.

    Silicon Flow provides affordable access to Flux models,
    with good support for both Chinese and English prompts.
    """

    API_URL = "https://api.siliconflow.cn/v1/images/generations"

    def __init__(self, api_key: str | None = None, model: str = "black-forest-labs/FLUX.1-schnell"):
        self.api_key = api_key or os.environ.get("SILICONFLOW_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError(
                "Silicon Flow API key is required. Set SILICONFLOW_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def generate(self, prompt: str, output_path: str, size: str = "1024x1024") -> GenerationResult:
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "image_size": size,
            "num_inference_steps": 20,
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
            raise RuntimeError(f"Silicon Flow API error {e.code}: {error_body}") from e

        image_info = body["images"][0]
        image_url = image_info.get("url")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if image_url:
            # Download the image from the returned URL
            img_req = urllib.request.Request(image_url)
            with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                with open(output_path, "wb") as f:
                    f.write(img_resp.read())
        else:
            # Fallback: base64 encoded response
            b64 = image_info.get("b64_json", "")
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64))

        return GenerationResult(
            image_path=output_path,
            prompt_used=prompt,
            provider="siliconflow",
            model=self.model,
        )
