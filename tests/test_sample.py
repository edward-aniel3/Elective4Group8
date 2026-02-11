"""
Sample test file to verify pytest setup
"""

import pytest


def test_sample_passing():
    """A simple passing test"""
    assert True


def test_basic_math():
    """Test basic arithmetic"""
    assert 2 + 2 == 4
    assert 10 - 5 == 5


def test_string_operations():
    """Test string operations"""
    text = "Hello, World!"
    assert "Hello" in text
    assert text.startswith("Hello")
    assert text.endswith("!")
