from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kaiten2planka",
    version="1.0.0",
    author="",
    author_email="",
    description="Migration tool from Kaiten to Planka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kaiten2planka",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "PyYAML>=6.0",
        "aiohttp>=3.8.0",
        "aiosqlite>=0.19.0",
        "tenacity>=8.2.0",
        "python-multipart>=0.0.6",
    ],
    entry_points={
        'console_scripts': [
            'kaiten2planka=kaiten2planka.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
