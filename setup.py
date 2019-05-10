#!/usr/bin/env python

import io
import os
from setuptools import find_packages, setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements


def local_path(*parts):
    base_folder = os.path.dirname(__file__)
    return os.path.join(base_folder, *parts)


def get_requirements(filename):
    install_reqs = parse_requirements(filename, session=False)
    return list(str(ir.req) for ir in install_reqs)


reqs = get_requirements("requirements.txt")
test_reqs = get_requirements("requirements-test.txt")

with io.open(local_path("README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='branchdb',
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    license="MIT License",
    description="Create a new version of your DB based off of your git branch",
    long_description=README,
    url='https://github.com/CalgaryMichael/branchdb',
    platforms=["any"],
    author="Calgary Michael",
    author_email="cseth.michael@gmail.com",
    scripts=[
        "bin/branchdb"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    install_requires=reqs,
    tests_require=test_reqs
)
