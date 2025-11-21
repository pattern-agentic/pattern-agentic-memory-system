#!/usr/bin/env python3
"""
Setup script for pattern-agentic-memory system.
Provides pip installation support alongside Poetry.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="pattern-agentic-memory",
    version="0.1.0",
    description="Adaptive Memory System with Identity Anchor Pattern - Never Fade to Black",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pattern Agentic",
    author_email="team@patternagentic.ai",
    url="https://github.com/pattern-agentic/pattern-agentic-memory-system",
    project_urls={
        "Documentation": "https://github.com/pattern-agentic/pattern-agentic-memory-system/tree/main/docs",
        "Source": "https://github.com/pattern-agentic/pattern-agentic-memory-system",
        "Tracker": "https://github.com/pattern-agentic/pattern-agentic-memory-system/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        # Zero required dependencies
    ],
    extras_require={
        "neo4j": ["neo4j>=5.14"],
        "dev": [
            "pytest>=8.0",
            "pytest-asyncio>=0.24",
            "pytest-cov>=6.0",
            "black>=24.0",
            "mypy>=1.0",
            "ruff>=0.8",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="memory ai-agents identity-preservation graph-rag adaptive-memory",
    license="MIT",
)
