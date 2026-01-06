"""Tests for OpenVTO prompt system."""

import pytest

from openvto.prompts import PromptLoader, load_prompt


class TestPromptLoader:
    """Tests for PromptLoader."""

    def test_load_avatar_prompt(self):
        """Test loading avatar prompt."""
        config = load_prompt("avatar", "studio_v1")
        assert config.name == "avatar"
        assert config.preset == "studio_v1"
        assert config.version == "1.0.0"
        assert "{subject}" in config.base_prompt

    def test_load_tryon_prompt(self):
        """Test loading tryon prompt."""
        config = load_prompt("tryon", "studio_v1")
        assert config.name == "tryon"
        assert "{clothing_description}" in config.base_prompt

    def test_load_videoloop_prompt(self):
        """Test loading videoloop prompt."""
        config = load_prompt("videoloop", "360_v1")
        assert config.name == "videoloop"
        assert "rotation" in config.full_config["presets"]["360_v1"]["motion"]["type"]

    def test_load_idle_videoloop(self):
        """Test loading idle preset."""
        config = load_prompt("videoloop", "idle_v1")
        assert config.preset == "idle_v1"

    def test_invalid_preset_raises_error(self):
        """Test that invalid preset raises PromptError."""
        from openvto.errors import PromptError

        with pytest.raises(PromptError, match="not found"):
            load_prompt("avatar", "nonexistent_preset")

    def test_invalid_prompt_raises_error(self):
        """Test that invalid prompt name raises PromptError."""
        from openvto.errors import PromptError

        with pytest.raises(PromptError, match="not found"):
            load_prompt("nonexistent_prompt")


class TestPromptConfig:
    """Tests for PromptConfig."""

    def test_render_with_variables(self):
        """Test rendering prompt with variable substitution."""
        config = load_prompt("avatar", "studio_v1")
        rendered = config.render(subject="a young woman with brown hair")
        assert "a young woman with brown hair" in rendered
        assert "{subject}" not in rendered

    def test_render_tryon_with_clothing(self):
        """Test rendering tryon prompt."""
        config = load_prompt("tryon", "studio_v1")
        rendered = config.render(
            subject="the model",
            clothing_description="a white linen shirt and blue jeans",
        )
        assert "white linen shirt" in rendered
        assert "the model" in rendered

    def test_render_missing_required_variable(self):
        """Test that missing required variable raises error."""
        from openvto.errors import PromptError

        config = load_prompt("avatar", "studio_v1")
        with pytest.raises(PromptError, match="Missing required variable"):
            config.render()  # Missing 'subject'

    def test_render_negative_prompt(self):
        """Test getting negative prompt."""
        config = load_prompt("avatar", "studio_v1")
        negative = config.render_negative()
        assert "deformed" in negative
        assert "blurry" in negative

    def test_style_components_included(self):
        """Test that style components are in rendered prompt."""
        config = load_prompt("avatar", "studio_v1")
        rendered = config.render(subject="test subject")
        # Should include lighting, background, etc from style
        assert "studio" in rendered.lower() or "lighting" in rendered.lower()


class TestPromptLoaderMethods:
    """Tests for PromptLoader utility methods."""

    def test_list_prompts(self):
        """Test listing available prompts."""
        loader = PromptLoader()
        prompts = loader.list_prompts()
        assert "avatar" in prompts
        assert "tryon" in prompts
        assert "videoloop" in prompts

    def test_list_presets(self):
        """Test listing presets for a prompt."""
        loader = PromptLoader()
        presets = loader.list_presets("avatar")
        assert "studio_v1" in presets
        assert "white_v1" in presets

    def test_list_videoloop_presets(self):
        """Test listing videoloop presets."""
        loader = PromptLoader()
        presets = loader.list_presets("videoloop")
        assert "360_v1" in presets
        assert "idle_v1" in presets
        assert "showcase_v1" in presets

    def test_get_version(self):
        """Test getting prompt version."""
        loader = PromptLoader()
        version = loader.get_version("avatar")
        assert version == "1.0.0"

    def test_caching(self):
        """Test that prompts are cached."""
        loader = PromptLoader()
        # Load twice
        config1 = loader.load("avatar", "studio_v1")
        config2 = loader.load("avatar", "white_v1")
        # Should use same cached raw config
        assert config1.full_config is config2.full_config

