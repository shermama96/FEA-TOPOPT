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
        self.localForceVector = []
        self.BC = []
        self.boundaryId = None
        self.traction = np.array([0, 0])
        
        
    def setLocalNodes(self, numOfXElems, numOfYElems):
        normalizedId = self.Id/numOfXElems
        if normalizedId%1 == 0:
            rowIdx = numOfYElems - mt.floor(normalizedId - 1)
        else:
            rowIdx = numOfYElems - mt.floor(normalizedId)
        
        BLid = self.Id + (numOfYElems - rowIdx)
        self.BLnode = node(BLid, [2*BLid - 1, 2*BLid], self.calcNodalCoords(1))
        
        BRid = self.BLnode.globalNodeNumber + 1
        self.BRnode = node(BRid, [2*BRid - 1, 2*BRid], self.calcNodalCoords(2))
        
        TLid = self.BLnode.globalNodeNumber + (numOfXElems + 1)
        self.TLnode = node(TLid, [2*TLid - 1, 2*TLid], self.calcNodalCoords(4))
        
        TRid = self.TLnode.globalNodeNumber + 1
        self.TRnode = node(TRid, [2*TRid - 1, 2*TRid], self.calcNodalCoords(3))
        
        
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
    
    def packageDOFs(self, offSet=True):
        temp = []
        for n in self.packageNodes():
            if offSet == True:
                temp.extend([n.xDOF - 1, n.yDOF - 1])
            else:
                temp.extend([n.xDOF, n.yDOF])
        return temp
    
    def setGauss(self):
        if len(self.packageNodes()) == 4:
            ptMag = 1/np.sqrt(3)
            gaussWeights = np.ones(4)
            gaussPoints = np.array([[-ptMag, -ptMag], [-ptMag, ptMag], [ptMag, -ptMag], [ptMag, ptMag]])
        else:
            raise(ValueError("No Gauss Point configuration for an element with", len(element.packageNodes()), "nodes"))
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
    
    # TODO
    # CHANGE SO FUNCTION BELOW ACTUALLY LOOKS FOR SPECIFIC BCS IN LIST
    
    def boundaryShapeFunction(self):
        try:
            if self.BC[0].edgeID == "top":
                N1, N2, N3, N4 = 0, 0, 1, 1
            elif self.BC[0].edgeID == "bottom":
                N1, N2, N3, N4 = 1, 1, 0, 0
            elif self.BC[0].edgeID == "right":
                N1, N2, N3, N4 = 1, 0, 0, 1
            elif self.BC[0].edgeID == "left":
                N1, N2, N3, N4 = 0, 1, 1, 0
                
            primary = [N1, 0, N2, 0, N3, 0, N4]
            return np.array([primary + [0], [0] + primary]).T
        except AttributeError:
            print("Oops, this element is either not on a boundary or has no BC assigned to it!")
            
    def prescribeDefaultTractions(self):
        for edge in self.boundaryId():
            if edge == "top":
                None
            elif edge == "bottom":
                None
            elif edge == "left":
                None
            elif edge == "right":
                None
            else:
                None
            
        
        
def test():
    testObject = element(1)
    return testObject
    
    
if __name__ == "__main__":
    res = test()
        