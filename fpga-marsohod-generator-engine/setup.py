#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="fpga-marsohod-generator-engine",
    packages=["fpga_marsohod_generator_engine"],
    version="0.0.1",
    description="Rendering engine for Marsohod FPGA-boards.",
    long_description="Rendering engine for Marsohod FPGA-boards.",
    author="Dmitriy Pchelkin | hell03end",
    author_email="hell03end@outlook.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    license="MIT License",
    platforms=["All"],
    python_requires=">=3.5"
)
