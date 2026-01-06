"""Prompt loader and manager for OpenVTO."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openvto.errors import PromptError

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent


@dataclass
class PromptConfig:
    """Configuration for a prompt template.

    Attributes:
        name: Prompt name (avatar, tryon, videoloop).
        version: Prompt version string.
        preset: Active preset name.
        base_prompt: The main prompt template.
        style: Style configuration dict.
        negative_prompt: Negative prompt string.
        variables: Variable definitions.
        full_config: Complete raw config dict.
    """

    name: str
    version: str
    preset: str
    base_prompt: str
    style: dict[str, str]
    negative_prompt: str
    variables: dict[str, Any]
    full_config: dict[str, Any]

    def render(self, **kwargs: Any) -> str:
        """Render the prompt with variable substitution.

        Args:
            **kwargs: Variable values to substitute.

        Returns:
            Rendered prompt string.

        Raises:
            PromptError: If required variable is missing.
        """
        # Check required variables
        for var_name, var_config in self.variables.items():
            if var_config.get("required", False) and var_name not in kwargs:
                raise PromptError(f"Missing required variable: {var_name}")

        # Build full prompt from components
        prompt_parts = [self.base_prompt]

        # Add style components
        for key, value in self.style.items():
            prompt_parts.append(value)

        # Join and substitute variables
        full_prompt = ", ".join(prompt_parts)

        # Simple variable substitution
        for key, value in kwargs.items():
            full_prompt = full_prompt.replace(f"{{{key}}}", str(value))

        return full_prompt

    def render_negative(self) -> str:
        """Get the negative prompt.

        Returns:
            Negative prompt string.
        """
        return self.negative_prompt


class PromptLoader:
    """Loader for prompt configuration files.

    Handles loading JSON prompt configs and selecting presets.
    """

    def __init__(self, prompts_dir: str | Path | None = None) -> None:
        """Initialize prompt loader.

        Args:
            prompts_dir: Directory containing prompt JSON files.
                        Defaults to the package's prompts directory.
        """
        self.prompts_dir = Path(prompts_dir) if prompts_dir else PROMPTS_DIR
        self._cache: dict[str, dict[str, Any]] = {}

    def _load_json(self, name: str) -> dict[str, Any]:
        """Load and cache a prompt JSON file."""
        if name not in self._cache:
            json_path = self.prompts_dir / f"{name}.json"
            if not json_path.exists():
                raise PromptError(f"Prompt file not found: {json_path}")

            try:
                with json_path.open("r") as f:
                    self._cache[name] = json.load(f)
            except json.JSONDecodeError as e:
                raise PromptError(f"Invalid JSON in prompt file {json_path}: {e}")

        return self._cache[name]

    def load(self, name: str, preset: str = "studio_v1") -> PromptConfig:
        """Load a prompt configuration.

        Args:
            name: Prompt name (avatar, tryon, videoloop).
            preset: Preset name to use.

        Returns:
            PromptConfig with the loaded configuration.

        Raises:
            PromptError: If prompt or preset not found.
        """
        config = self._load_json(name)

        if preset not in config.get("presets", {}):
            available = list(config.get("presets", {}).keys())
            raise PromptError(
                f"Preset '{preset}' not found for prompt '{name}'. "
                f"Available presets: {available}"
            )

        preset_config = config["presets"][preset]

        return PromptConfig(
            name=config["name"],
            version=config["version"],
            preset=preset,
            base_prompt=preset_config["base_prompt"],
            style=preset_config.get("style", {}),
            negative_prompt=config.get("negative_prompt", ""),
            variables=config.get("variables", {}),
            full_config=config,
        )

    def list_prompts(self) -> list[str]:
        """List available prompt names.

        Returns:
            List of prompt names (without .json extension).
        """
        return [
            p.stem for p in self.prompts_dir.glob("*.json") if p.stem != "__init__"
        ]

    def list_presets(self, name: str) -> list[str]:
        """List available presets for a prompt.

        Args:
            name: Prompt name.

        Returns:
            List of preset names.
        """
        config = self._load_json(name)
        return list(config.get("presets", {}).keys())

    def get_version(self, name: str) -> str:
        """Get the version of a prompt.

        Args:
            name: Prompt name.

        Returns:
            Version string.
        """
        config = self._load_json(name)
        return config.get("version", "unknown")


# Default loader instance
_default_loader: PromptLoader | None = None


def get_loader() -> PromptLoader:
    """Get the default prompt loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader


def load_prompt(name: str, preset: str = "studio_v1") -> PromptConfig:
    """Convenience function to load a prompt.

    Args:
        name: Prompt name (avatar, tryon, videoloop).
        preset: Preset name to use.

    Returns:
        PromptConfig with the loaded configuration.
    """
    return get_loader().load(name, preset)

