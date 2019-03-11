#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from setup_qt import build_qt
from timmu import __version__

#PyPI guide: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='timmu',
    version = __version__,
    description="GUI for tim (command line time logger with hledger backend for number crunching)",
    long_description=(read('README.md') + "\n\n" + 
                      read("AUTHORS.md")),
    license="MIT",
    author="Alex Beimler",
    author_email="alex-beimler@web.de",
    url="https://github.com/abeimler/tim",
    platforms=["Any"],
    install_requires=[
        'argparse>=1.4.0',
        'parsedatetime>=2.4',
        'colorama>=0.4.1',
        'pyyaml>=3.13',
        'tzlocal>=1.5.1',
        'pytz>=2018.9',
        'duration>=1.1.1',
        'PyQt5',
        'Qt.py'
    ],
    packages=find_packages(exclude=['gif', 'site', 'test']),
    package_data={
        'timmu': [
            '*.ui',
            '*.qrc',
            'languages/*.ts',
            'languages/*.qm',
        ],
    },
    entry_points={
        'console_scripts': ['tim=timmu.tim.__main__:main'],
        'gui_scripts': [
            'timmu=timmu.__main__:main',
        ],
    },
    options={
        'build_qt': {
            'packages': ['timmu'],
            'bindings': 'PyQt5',           # optional ('PyQt5' is default)
            'replacement_bindings': 'Qt',  # optional (for Qt.py wrapper usage)
        },
    },
    cmdclass={
        'build_qt': build_qt,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)

