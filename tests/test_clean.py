#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import pytest
"""Run doctests and unittests for talkingdata.clean module"""

import doctest
import talkingdata.clean

__author__ = "Hobson Lane"
__copyright__ = "Hobson Lane"
__license__ = "mit"


def test_clean():
    assert doctest.testmod(talkingdata.clean, optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS).failed == 0
    # with pytest.raises(AssertionError):
    #     fib(-10)
