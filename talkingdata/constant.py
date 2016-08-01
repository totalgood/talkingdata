#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Constants like paths to data and log files

>>> os.path.isdir(DATA_DIR)
True
>>> os.path.isdir()
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_DIR = os.path.abspath(os.path.dirname(PACKAGE_DIR))
DATA_DIR = None
for DATA_DIR in (os.getenv(DATA_DIR), '/var/local/data', os.path.join(REPO_DIR, 'data')):
    if DATA_DIR and os.path.isdir(DATA_DIR):
        break
DATA_DIR_TALKING_DATA = os.path.join(DATA_DIR, 'kaggle', '2016-09-31-talking-data')
