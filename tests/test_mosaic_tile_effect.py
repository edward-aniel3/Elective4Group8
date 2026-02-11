"""Tests for Mosaic Tile Effect module (mosaic_tile_effect)."""

import cv2
import numpy as np
import pytest
from elective4group8.mosaic_tile_effect import blockify_image


def test_blockify_image_shape():
    img = np.ones((32, 32, 3), dtype=np.uint8) * 255
    blockified = blockify_image(img, block_size=8)
    assert blockified.shape == img.shape


def test_blockify_uniform_image():
    # Uniform white → blockification changes nothing
    img = np.ones((64, 64, 3), dtype=np.uint8) * 255
    blockified = blockify_image(img, block_size=8)
    assert np.all(blockified == 255)


def test_blockify_creates_blocks():
    # After blockification, neighbouring pixels within a block should be identical
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    bs = 16
    blockified = blockify_image(img, block_size=bs)

    # Check one block
    block = blockified[0:bs, 0:bs]
    assert np.all(block == block[0, 0])
