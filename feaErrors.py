# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:24:52 2020

@author: mns72
"""


class Error(Exception):
    pass

class InvalidMeshConfig(Error):
    pass

class ElementOutOfBoundsError(Error):
    pass

class InvalidBCTypeError(Error):
    pass
