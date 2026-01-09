"""Tests for OpenVTO example assets module."""

from pathlib import Path

import pytest

from openvto import example


class TestListClothesCategories:
    """Tests for list_clothes_categories function."""

    def test_returns_list_of_categories(self):
        """Test that it returns the expected categories."""
        categories = example.list_clothes_categories()
        assert isinstance(categories, list)
        assert "jackets" in categories
        assert "pants" in categories
        assert "shirts" in categories

    def test_categories_are_sorted(self):
        """Test that categories are returned in sorted order."""
        categories = example.list_clothes_categories()
        assert categories == sorted(categories)


class TestListClothesItems:
    """Tests for list_clothes_items function."""

    def test_returns_indices_and_views(self):
        """Test that it returns indices and views."""
        items = example.list_clothes_items("jackets")
        assert "indices" in items
        assert "views" in items
        assert isinstance(items["indices"], list)
        assert isinstance(items["views"], list)

    def test_jackets_have_four_items(self):
        """Test that jackets category has 4 items."""
        items = example.list_clothes_items("jackets")
        assert items["indices"] == [1, 2, 3, 4]

    def test_jackets_have_front_and_back_views(self):
        """Test that jackets have front and back views."""
        items = example.list_clothes_items("jackets")
        assert "front" in items["views"]
        assert "back" in items["views"]

    def test_invalid_category_raises_value_error(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Unknown clothing category"):
            example.list_clothes_items("nonexistent")


class TestClothes:
    """Tests for clothes function."""

    def test_all_jackets_returns_four_entries(self):
        """Test that clothes('jackets') returns 4 entries."""
        all_jackets = example.clothes("jackets")
        assert len(all_jackets) == 4
        for item in all_jackets:
            assert "i" in item
            assert "front" in item
            assert "back" in item
            assert isinstance(item["front"], Path)
            assert isinstance(item["back"], Path)

    def test_specific_item_returns_both_views(self):
        """Test that clothes('jackets', i=2) returns front and back."""
        jacket = example.clothes("jackets", i=2)
        assert isinstance(jacket, dict)
        assert "front" in jacket
        assert "back" in jacket
        assert isinstance(jacket["front"], Path)
        assert isinstance(jacket["back"], Path)

    def test_specific_view_returns_single_path(self):
        """Test that clothes('jackets', i=2, view='front') returns single path."""
        path = example.clothes("jackets", i=2, view="front")
        assert isinstance(path, Path)
        assert path.exists()
        assert "2_front.jpg" in str(path)

    def test_back_view_returns_existing_path(self):
        """Test that back view returns existing path."""
        path = example.clothes("pants", i=1, view="back")
        assert isinstance(path, Path)
        assert path.exists()
        assert "1_back.jpg" in str(path)

    def test_invalid_category_raises_value_error(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Unknown clothing category"):
            example.clothes("invalid_category")

    def test_invalid_view_raises_value_error(self):
        """Test that invalid view raises ValueError."""
        with pytest.raises(ValueError, match="Invalid view"):
            example.clothes("jackets", i=1, view="side")

    def test_invalid_item_index_raises_file_not_found(self):
        """Test that invalid item index raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Clothing asset not found"):
            example.clothes("jackets", i=99)

    def test_view_without_i_raises_value_error(self):
        """Test that specifying view without i raises ValueError."""
        with pytest.raises(
            ValueError, match="Cannot specify 'view' without specifying 'i'"
        ):
            example.clothes("jackets", view="front")

    def test_return_type_bytes(self):
        """Test that return_type='bytes' returns bytes."""
        data = example.clothes("jackets", i=1, view="front", return_type="bytes")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_all_categories_work(self):
        """Test that all categories return valid results."""
        for category in ["jackets", "pants", "shirts"]:
            items = example.clothes(category)
            assert len(items) == 4


class TestAvatar:
    """Tests for avatar function."""

    def test_avatar_returns_path(self):
        """Test that avatar returns a valid path."""
        path = example.avatar(i=1)
        assert isinstance(path, Path)
        assert path.exists()
        assert "1.png" in str(path)

    def test_invalid_avatar_raises_file_not_found(self):
        """Test that invalid avatar index raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Avatar not found"):
            example.avatar(i=99)

    def test_return_type_bytes(self):
        """Test that return_type='bytes' returns bytes."""
        data = example.avatar(i=1, return_type="bytes")
        assert isinstance(data, bytes)
        assert len(data) > 0


class TestPerson:
    """Tests for person function."""

    def test_person_posture_returns_path(self):
        """Test that person with posture returns a valid path."""
        path = example.person(i=1, kind="posture")
        assert isinstance(path, Path)
        assert path.exists()
        assert "1_posture.jpg" in str(path)

    def test_person_selfie_returns_path(self):
        """Test that person with selfie returns a valid path."""
        path = example.person(i=1, kind="selfie")
        assert isinstance(path, Path)
        assert path.exists()
        assert "1_selfie.jpg" in str(path)

    def test_invalid_kind_raises_value_error(self):
        """Test that invalid kind raises ValueError."""
        with pytest.raises(ValueError, match="Invalid kind"):
            example.person(i=1, kind="invalid")  # type: ignore[arg-type]

    def test_invalid_person_index_raises_file_not_found(self):
        """Test that invalid person index raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Person photo not found"):
            example.person(i=99)

    def test_return_type_bytes(self):
        """Test that return_type='bytes' returns bytes."""
        data = example.person(i=1, kind="posture", return_type="bytes")
        assert isinstance(data, bytes)
        assert len(data) > 0


class TestReturnTypePil:
    """Tests for PIL return type (requires pillow)."""

    @pytest.fixture
    def pil_available(self):
        """Check if PIL is available."""
        try:
            from PIL import Image  # noqa: F401

            return True
        except ImportError:
            return False

    def test_clothes_pil_return_type(self, pil_available):
        """Test clothes with return_type='pil'."""
        if not pil_available:
            pytest.skip("Pillow not installed")

        from PIL import Image

        img = example.clothes("jackets", i=1, view="front", return_type="pil")
        assert isinstance(img, Image.Image)

    def test_avatar_pil_return_type(self, pil_available):
        """Test avatar with return_type='pil'."""
        if not pil_available:
            pytest.skip("Pillow not installed")

        from PIL import Image

        img = example.avatar(i=1, return_type="pil")
        assert isinstance(img, Image.Image)

    def test_person_pil_return_type(self, pil_available):
        """Test person with return_type='pil'."""
        if not pil_available:
            pytest.skip("Pillow not installed")

        from PIL import Image

        img = example.person(i=1, kind="posture", return_type="pil")
        assert isinstance(img, Image.Image)


class TestImportFromOpenvto:
    """Test that example can be imported from openvto."""

    def test_import_example_from_openvto(self):
        """Test that example is importable from openvto package."""
        from openvto import example

        assert hasattr(example, "clothes")
        assert hasattr(example, "avatar")
        assert hasattr(example, "person")
        assert hasattr(example, "list_clothes_categories")
        assert hasattr(example, "list_clothes_items")
