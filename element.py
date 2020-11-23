# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 15:36:22 2020

@author: mns72
"""

from node import node
import math as mt
import numpy as np
import numpy.linalg as npl

class element():

    def __init__(self, Id, indices, xLength, yLength):
        self.Id = Id
        self.densityBool = 1
        self.meshIndices = indices
        self.xLength = xLength
        self.yLength = yLength
        self.localStiffMat = []
        self.localForceMat = []
        
    
    def setLocalNodes(self, numOfXElems, numOfYElems):
        normalizedId = self.Id/numOfXElems
        if normalizedId%1 == 0:
            rowIdx = numOfYElems - mt.floor(normalizedId - 1)
        else:
            rowIdx = numOfYElems - mt.floor(normalizedId)
        
        self.BLnode = node(self.Id + (numOfYElems - rowIdx), self.calcNodalCoords(1))
        self.BRnode = node(self.BLnode.globalNodeNumber + 1, self.calcNodalCoords(2))
        self.TLnode = node(self.BLnode.globalNodeNumber + (numOfXElems + 1), self.calcNodalCoords(4))
        self.TRnode = node(self.TLnode.globalNodeNumber + 1, self.calcNodalCoords(3))
        
    def calcNodalCoords(self, localIndex):
         xCoord = self.meshIndices[1] * self.xLength
         yCoord = self.meshIndices[0] * self.yLength
         
         if localIndex == 2:
             xCoord = xCoord + self.xLength
         elif localIndex == 3:
             xCoord = xCoord + self.xLength
             yCoord = yCoord + self.yLength
         elif localIndex == 4:
             yCoord = yCoord + self.yLength
         return [xCoord, yCoord]
        
        
    def packageNodes(self):
        return [self.BLnode, self.BRnode, self.TRnode, self.TLnode]
    
    def setGauss(self, gaussPoints, gaussWeights):
        self.gaussPoints = gaussPoints
        self.gaussWeights = gaussWeights
        
    
    def packageNodeIds(self):
        nodes = self.packageNodes()
        res = np.zeros(len(nodes))
        for n in nodes:
            res[nodes.index(n)] = n.globalNodeNumber
        return res
    
    def packageNodalCoords(self):
        coordMat = []
        for i in self.packageNodes():
            coordMat.append(np.array([i.xCoord, i.yCoord]))
        return np.array(coordMat)
            
        
        
def test():
    testObject = element(1)
    return testObject
    
    
if __name__ == "__main__":
    res = test()
        