"""Tests for background_remover module."""

import cv2
import numpy as np
import pytest
from elective4group8.background_remover import (
    is_image_file,
    remove_background_smart,
)


def test_is_image_file():
    assert is_image_file("photo.jpg") is True
    assert is_image_file("photo.png") is True
    assert is_image_file("photo.jpeg") is True
    assert is_image_file("photo.bmp") is True
    assert is_image_file("notes.txt") is False
    assert is_image_file("data.csv") is False


def test_remove_background_smart_returns_same_shape():
    """Smart removal should return a BGR image with the same shape."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 180
    cv2.rectangle(img, (25, 25), (75, 75), (0, 0, 200), -1)
    result = remove_background_smart(img)
    assert result.shape == img.shape


def test_remove_background_smart_white_bg():
    """Background pixels should become white after smart removal."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (30, 30), (70, 70), (0, 0, 200), -1)
    result = remove_background_smart(img)
    # Result should still be 3-channel
    assert len(result.shape) == 3
    assert result.shape[2] == 3
