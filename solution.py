# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 20:04:46 2020

@author: mns72
"""
from setup import setup
from boundaryCondition import boundaryCondition
import numpy as np
import numpy.linalg as npl
def swap(o, idx1, idx2, colOrRow):
    if isinstance(o, list) or (isinstance(o, np.ndarray) and len(np.shape(o)) == 1):
        tempVals = o[idx2]
        o[idx2] = o[idx1]
        o[idx1] = tempVals
    else:
        if colOrRow == "row":
            tempVals = o[idx2, :]
            o[idx2,:] = o[idx1,:]
            o[idx1,:] = tempVals
        elif colOrRow == "col":
            tempVals = o[:,idx2]
            o[:,idx2] = o[:,idx1]
            o[:,idx1] = tempVals
        else:
            raise(NameError("Invalid identifier, choose from row or col!"))
    return o
        
class solution():
    
    def __init__(self, setupObject):
        self.setup = setupObject
        self.K = setupObject.globalStiffnessMatrix
        self.F = setupObject.globalForceVector
        self.D = setupObject.globalDisplacementVector
        self.partitionIdx = None
        self.KE = []
        self.KF = []
        self.KEF = []
        self.DE = []
        self.DF = []
        self.R = []
        self.essentialIndices = []
        
        
    def arrangeSystem(self):
        moveCtr = 0
        for i in range(len(self.D)):
            if self.D[i] != None:
                self.essentialIndices.append(i)
                self.D = swap(self.D, i, moveCtr, "row")
                self.F = swap(self.F, i, moveCtr, "row")
                self.K = swap(self.K, i, moveCtr, "row")
                self.K = swap(self.K, i, moveCtr, "col")
                moveCtr += 1
        self.partitionIdx = moveCtr
        
    def partition(self):
        self.KE = self.K[0:self.partitionIdx, 0:self.partitionIdx]
        self.KF = self.K[self.partitionIdx+1:-1, self.partitionIdx+1:-1]
        self.KEF = self.K[0:self.partitionIdx, self.partitionIdx+1:-1]
        self.FE = self.F[0:self.partitionIdx]
        self.FF = self.F[self.partitionIdx+1:-1]
        self.DE = np.array(self.D[0:self.partitionIdx])
        
    def solve(self):
        if self.partitionIdx == 0:
            self.DF	= npl.inv(self.KF) @ self.FF
        else:
            self.DF	= npl.inv(self.KF) @ ( self.FF - self.KEF.T @ self.DE)
            
        if self.partitionIdx == 0:
            self.R = self.KEF @ self.DF;
        else:
            self.R = self.KE @ self.DE + self.KEF @ self.DF - self.FE
            
    def unpack(self):
        for idx in self.essentialIndices:
            tempNode = self.setup.mesh.nodeDict[idx]
            
            if tempNode != self.setup.mesh.nodeDict[idx-1]:
                tempNode.xDisplacement = 
 
# % reconstruct the global solution U
# d(essDOF)=d_E;                
# d(freeDOF)=d_F;
    
    
    
    
def test():
    setupObject = setup()
    setupObject.domain.setDomainParams(10, 10, 1, 2800, 70E9, .3)
    setupObject.mesh.configMesh(xFactor=10, yFactor=10, meshType="NpE")
    setupObject.mesh.generateMesh(setupObject.domain)
    boundaryCondition(setupObject, "force", "right", xMag=100)
    boundaryCondition(setupObject, "constraint", "left")
    setupObject.globalAssembly()
    solutionObject = solution(setupObject)
    solutionObject.arrangeSystem()
    solutionObject.partition()
    solutionObject.solve()
    solutionObject.setup.mesh.nodeDofDictionary()
    return solutionObject
      
if __name__ == "__main__":
    res = test()
                
                
                