"""
Tests for the calculator module
"""

import pytest
import sys
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from elective4group8.calculator import add, subtract, multiply, divide


def test_add():
    """Test addition function"""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    """Test subtraction function"""
    assert subtract(5, 3) == 2
    assert subtract(10, 15) == -5
    assert subtract(0, 0) == 0


def test_multiply():
    """Test multiplication function"""
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 100) == 0


def test_divide():
    """Test division function"""
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3
    assert divide(7, 2) == 3.5


def test_divide_by_zero():
    """Test that dividing by zero raises an error"""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
