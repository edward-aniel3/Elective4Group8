"""Tests for minecraft_filter module."""

import cv2
import numpy as np
import pytest
from elective4group8.minecraft_filter import minecraft_filter


def test_minecraft_filter_shape():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    out = minecraft_filter(img, block_size=10)
    assert out.shape == img.shape


def test_minecraft_filter_blockification():
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    img[0:10, 0:10]   = [255, 0, 0]     # block mapped to closest palette
    img[10:20, 10:20] = [0, 255, 0]     # another colour

    out = minecraft_filter(img, block_size=10)

    # Each 10×10 block should be uniform (all pixels same colour)
    top_left = out[0:10, 0:10]
    assert np.all(top_left == top_left[0, 0])

    bottom_right = out[10:20, 10:20]
    assert np.all(bottom_right == bottom_right[0, 0])


def test_minecraft_filter_uniform_input():
    # Pure white → should map to Snow (255, 255, 255)
    img = np.ones((30, 30, 3), dtype=np.uint8) * 255
    out = minecraft_filter(img, block_size=10)
    assert np.all(out == 255)
