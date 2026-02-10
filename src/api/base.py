"""Base class for image generation API clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result from an image generation API call."""
    image_path: str
    prompt_used: str
    provider: str
    model: str
    revised_prompt: str | None = None


class ImageAPIClient(ABC):
    """Abstract base class for image generation API clients."""

    @abstractmethod
    def generate(self, prompt: str, output_path: str, size: str = "1024x1024") -> GenerationResult:
        """Generate an image from a text prompt.

        Args:
            prompt: The text prompt for image generation.
            output_path: Path to save the generated image.
            size: Image dimensions (e.g., "1024x1024").

        Returns:
            GenerationResult with the saved image path and metadata.
        """
        ...
