"""Setup configuration for kaiten2planka."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kaiten2planka",
    version="1.0.0",
    author="Migration Team",
    author_email="migration@example.com",
    description="Production-ready migration tool from Kaiten to Planka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/kaiten2planka",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "kaiten2planka=kaiten2planka.cli:migrate",
        ],
    },
    include_package_data=True,
    package_data={
        "kaiten2planka": ["*.yaml", "*.yml"],
    }
)
