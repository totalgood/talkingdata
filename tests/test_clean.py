#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import pytest
from talkingdata.skeleton import fib

import doctest
import talkingdata

__author__ = "Hobson Lane"
__copyright__ = "Hobson Lane"
__license__ = "none"


def test_clean():
    assert doctest.testmod(talkingdata, doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS) 
    # with pytest.raises(AssertionError):
    #     fib(-10)
