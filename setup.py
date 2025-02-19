#!/usr/bin/env python3
from setuptools import setup, find_packages
from pathlib import Path

# Version handling
VERSION = "1.4"

# Common setup configuration
setup(
    name='mtkclient',
    version=VERSION,
    packages=find_packages(),
    description='Mediatek reverse engineering and flashing tools',
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author='B. Kerler',
    author_email='info@revskills.de',
    url='https://github.com/bkerler/mtkclient',
    project_urls={
        "Bug Tracker": "https://github.com/bkerler/mtkclient/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='mediatek flash-tool reverse-engineering',
    license='MIT',
    python_requires=">=3.7",
    install_requires=[
        'colorama>=0.4.4',
        'pyusb>=1.2.1',
        'pycryptodome>=3.17',
    ],
    scripts=['mtk', 'stage2'],  # Keep existing script files
    data_files=[
        ('', ['LICENSE', 'README.md']),
    ],
    include_package_data=True,
    zip_safe=False
)