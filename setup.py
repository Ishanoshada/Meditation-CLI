from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="meditation",
    version="3.0.0",
    description="A colorful, animated, cross-platform terminal meditation companion.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ishan Oshada",
    author_email="ic31908@gmail.com",
    url="https://github.com/ishanoshada/Meditation-CLI",
    project_urls={
        "Source": "https://github.com/ishanoshada/Meditation-CLI",
        "Bug Tracker": "https://github.com/ishanoshada/Meditation-CLI/issues",
    },
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "meditation=meditation.cli:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Utilities",
        "Intended Audience :: End Users/Desktop",
    ],
    keywords="meditation cli terminal mindfulness breathing ascii-art 3d",
    python_requires=">=3.7",
    license="MIT",
)
