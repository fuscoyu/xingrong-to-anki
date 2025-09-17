#!/usr/bin/env python3
"""
Setup script for xingrong-to-anki
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="xingrong-to-anki",
    version="1.0.0",
    author="xingrong-to-anki contributors",
    description="Convert Xingrong English lesson PDFs to Anki flashcards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xingrong-to-anki",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "xingrong-to-anki=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
