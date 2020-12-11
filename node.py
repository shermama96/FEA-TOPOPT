# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 15:35:41 2020

@author: mns72
"""

class node():
    
    def __init__(self, globalNodeNumber, DOFs, coords):
        self.globalNodeNumber = globalNodeNumber
        self.xDOF = DOFs[0]
        self.yDOF = DOFs[1]
        self.DOFsper = len(DOFs)
        self.xCoord = coords[0]
        self.yCoord = coords[1]
        self.xDisplacement = None
        self.yDisplacement = None 
        self.xForce = None
        self.yForce = None
        

        
        
        