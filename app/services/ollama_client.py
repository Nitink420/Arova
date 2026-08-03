# app/services/ollama_client.py
"""
AROVA Ollama HTTP Client

Pure HTTP client for communicating with the Ollama API.
Single responsibility: HTTP transport only.

No business logic. No prompt building. No safety filtering.
No subprocess. No ollama serve. No hardcoded URLs.

The endpoint URL is fully configurable via .env (OLLAMA_API_URL).

Usage:
    from app.services.ollama_client import OllamaClient
    client = OllamaClient()
    if client.health_check():
        response = client.generate("llama3.2:1b", "Hello", options={})
"""

import json
from typing import Generator, Optional

import requests

from app.core.config import Config
from app.core.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """
    HTTP client for the Ollama REST API.

    All configuration (URL, timeout) comes from Config singleton.
    This class never starts, stops, or manages the Ollama process.
    """

    def __init__(self):
        config = Config()
        self.base_url = config.OLLAMA_API_URL
        self.timeout = config.OLLAMA_TIMEOUT
        self._generate_url = f"{self.base_url}/api/generate"

    def health_check(self) -> bool:
        """
        Check if the Ollama server is reachable.

        Sends a GET request to the base URL.

        Returns:
            True if the server responds with HTTP 200, False otherwise.
        """
        try:
            response = requests.get(self.base_url, timeout=3)
            if response.status_code == 200:
                logger.info("Ollama server is active at %s", self.base_url)
                return True
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama server unreachable at %s", self.base_url)
        except requests.exceptions.Timeout:
            logger.warning("Ollama server timeout at %s", self.base_url)
        except Exception as e:
            logger.warning("Ollama health check failed: %s", e)

        return False

    def generate(
        self,
        model: str,
        prompt: str,
        options: Optional[dict] = None,
    ) -> Optional[str]:
        """
        Send a non-streaming generation request to Ollama.

        Args:
            model: Model name (e.g., "llama3.2:1b").
            prompt: The prompt text.
            options: Optional inference options (num_ctx, temperature, etc.).

        Returns:
            Generated text response, or None on failure.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            payload["options"] = options

        try:
            response = requests.post(
                self._generate_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.ConnectionError:
            logger.error(
                "Cannot connect to Ollama at %s. "
                "Verify OLLAMA_API_URL in .env and that Ollama is running.",
                self.base_url,
            )
        except requests.exceptions.Timeout:
            logger.error(
                "Ollama request timed out after %ds. "
                "Consider increasing OLLAMA_TIMEOUT.",
                self.timeout,
            )
        except requests.exceptions.HTTPError as e:
            logger.error("Ollama HTTP error: %s", e)
        except Exception as e:
            logger.error("Ollama generate failed: %s", e)

        return None

    def generate_stream(
        self,
        model: str,
        prompt: str,
        options: Optional[dict] = None,
    ) -> Generator[str, None, None]:
        """
        Send a streaming generation request to Ollama.

        Yields accumulated text as tokens arrive.

        Args:
            model: Model name (e.g., "llama3.2:1b").
            prompt: The prompt text.
            options: Optional inference options.

        Yields:
            Accumulated response text after each token.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }
        if options:
            payload["options"] = options

        try:
            response = requests.post(
                self._generate_url,
                json=payload,
                stream=True,
                timeout=self.timeout,
            )
            response.raise_for_status()

            accumulated_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    accumulated_text += token
                    yield accumulated_text

        except requests.exceptions.ConnectionError:
            logger.error(
                "Cannot connect to Ollama at %s for streaming. "
                "Verify OLLAMA_API_URL in .env.",
                self.base_url,
            )
        except requests.exceptions.Timeout:
            logger.error(
                "Ollama streaming request timed out after %ds.",
                self.timeout,
            )
        except Exception as e:
            logger.error("Ollama streaming failed: %s", e)
