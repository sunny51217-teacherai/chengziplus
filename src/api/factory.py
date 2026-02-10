"""Factory for creating image generation API clients."""

from .base import ImageAPIClient
from .openai_client import OpenAIClient
from .stability_client import StabilityClient
from .siliconflow_client import SiliconFlowClient

PROVIDERS = {
    "openai": OpenAIClient,
    "stability": StabilityClient,
    "siliconflow": SiliconFlowClient,
}


def create_client(provider: str, **kwargs) -> ImageAPIClient:
    """Create an image generation client for the given provider.

    Args:
        provider: One of "openai", "stability", "siliconflow".
        **kwargs: Additional arguments passed to the client constructor.

    Returns:
        An ImageAPIClient instance.
    """
    cls = PROVIDERS.get(provider)
    if cls is None:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider}'. Available: {available}")
    return cls(**kwargs)
