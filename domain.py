# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:13:29 2020

@author: mns72
"""

class domain():
    
    def __init__(self):
        self.length = None
        self.height = None
        self.depth = None
        self.density = None
        self.youngsMod = None
        self.pRatio = None
        self.mass = None
        self.shearMod = None
        
    def setDomainParams(self, length, height, depth, density, youngsMod, pRatio):
        self.length = length
        self.height = height
        self.depth = depth
        self.density = density
        self.youngsMod = youngsMod
        self.pRatio = pRatio
        self.mass = length*height*depth*density
        self.shearMod = youngsMod/((2*(1 + pRatio)))
        