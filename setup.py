#!/usr/bin/env python
# Install ETA
#
# Copyright 2017, Voxel51, LLC
# voxel51.com
#
from setuptools import setup, find_packages

from eta import constants


setup(
    name=constants.NAME,
    version=constants.VERSION,
    description=constants.DESCRIPTION,
    author=constants.AUTHOR,
    author_email=constants.CONTACT,
    url=constants.URL,
    license=constants.LICENSE,
    packages=find_packages(),
)
