# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 15:14:03 2020

@author: mns72
"""

# TODO
# Detect boundary nodes
import mesh
import domain
import numpy as np
import numpy.linalg as npl
import itertools

def gaussQuad(element):
    if len(element.packageNodes()) == 4:
        ptMag = 1/np.sqrt(3)
        gaussWeights = np.ones(4)
        gaussPoints = np.array([[-ptMag, -ptMag], [-ptMag, ptMag], [ptMag, -ptMag], [ptMag, ptMag]])
        element.setGauss(gaussPoints, gaussWeights)
    else:
        ValueError("No Gauss Point configuration for an element with", len(element.packageNodes()), "nodes")
        
def buildShapeMatrix(gaussPoints):
    # TODO
    # CHANGE THE LENGTH VALUE
    if len(gaussPoints) == 2:
        res = .25*np.array([(1 - gaussPoints[0])*(1 - gaussPoints[1]), (1 + gaussPoints[0])*(1 - gaussPoints[1]),\
                            (1 + gaussPoints[0])*(1 + gaussPoints[1]), (1 - gaussPoints[0])*(1 + gaussPoints[1])])
    return res

def buildShapeDerivMatrix(gaussPoints):
    # TODO
    # CHANGE THE LENGTH VALUE
    if len(gaussPoints) == 2:
        res = .25*np.array([[-(1 - gaussPoints[1]), (1 - gaussPoints[1]), (1 + gaussPoints[1]), -(1 + gaussPoints[1])],\
                            [-(1 - gaussPoints[0]), -(1 + gaussPoints[0]), (1 + gaussPoints[0]), (1 - gaussPoints[0])]])
    return res

def quadBMatrix(jacobianMatrix, derivShapeMat):
    temp = npl.inv(jacobianMatrix)@derivShapeMat
    B = np.array([[temp[0][0], 0, temp[0][1], 0, temp[0][2], 0, temp[0][3], 0],\
                  [0, temp[1][0], 0, temp[1][1], 0, temp[1][2], 0, temp[1][3]],\
                  [temp[1][0], temp[0][0], temp[1][1], temp[0][1], temp[1][2], temp[0][2], temp[1][3], temp[0][3]]])
    return B

class setup():
    
    def __init__(self):
        self.mesh = mesh.mesh()
        self.domain = domain.domain()
        
    def elastConstMat(self):
        E = self.domain.youngsMod
        v = self.domain.pRatio
        return (E/(1 - v**2))*np.array(([1, v, 0], [v, 1, 0], [0, 0, .5*(1 - v)]))
    
    def localConstruction(self, element):
        nodalCoords = element.packageNodalCoords()
        element.localStiffMat = np.zeros((8,8))
        idx = 0
        for i in element.gaussPoints:
            shapeMat = buildShapeMatrix(i)
            derivShapeMat = buildShapeDerivMatrix(i)
            jacobian = derivShapeMat@nodalCoords
            bMat = quadBMatrix(jacobian, derivShapeMat)
            transdormedCoords = shapeMat@nodalCoords
            
            tempStiff = (bMat.T @ self.elastConstMat() @ bMat)*element.gaussWeights[idx]*npl.det(jacobian)
            element.localStiffMat = element.localStiffMat + tempStiff
            idx += 1
    
    def globalAssembly(self):
        for el in list(itertools.chain(*self.mesh.elements)):
            gaussQuad(el)
            self.localConstruction(el)
            
            
        
def test():
    setupObject = setup()
    setupObject.domain.setDomainParams(10, 10, 1, 2800, 70E9, .3)
    setupObject.mesh.configMesh(xFactor=3, yFactor=4, meshType="NpE")
    setupObject.mesh.generateMesh(setupObject.domain)
    setupObject.globalAssembly()
    return setupObject
      
if __name__ == "__main__":
    res = test()
