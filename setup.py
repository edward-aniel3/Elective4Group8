"""
Setup configuration for elective4group8 package
"""

from setuptools import setup, find_packages

setup(
    name="elective4group8",
    version="0.1.0",
    description="Elective 4 Group 8 Project",
    author="Group 8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
)
