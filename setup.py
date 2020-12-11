# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 15:14:03 2020

@author: mns72
"""

# TODO
# Turn of gravity and calc body forces
# Convert tractions to force
# Potentially change traction component ordering based o normal vector direction for a given edge ID
# Deal with corner elements if a traction is prescribed on bottom and left edge

import mesh
import domain
from boundaryCondition import boundaryCondition
import numpy as np
import numpy.linalg as npl
import itertools

       
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
    
    def __init__(self, gravity=True, units="MKS"):
        self.mesh = mesh.mesh()
        self.domain = domain.domain()
        self.forces = []
        self.constraints = []
        self.globalStiffnessMatrix = np.array([])
        self.globalForceVector = []
        self.globalDisplacementVector = []
        
    def elastConstMat(self):
        E = self.domain.youngsMod
        v = self.domain.pRatio
        return (E/(1 - v**2))*np.array(([1, v, 0], [v, 1, 0], [0, 0, .5*(1 - v)]))
    
    # TODO
    # Consider moving to element class
    def localConstruction(self, el):
        nodalCoords = el.packageNodalCoords()
        el.localStiffMat = np.zeros([i*len(el.packageNodes())*el.BLnode.DOFsper for i in [1, 1]])
        
        if (el in self.mesh.boundary) and len(el.BC) > 0 and el.BC[0].kind == "force":
            # if not element.BC:
            #     element.prescribeDefaultTractions()
            el.localForceVector = el.boundaryShapeFunction() @ el.traction
            
            # for n in el.packageNodes():
            #     idx = 2*el.packageNodes().index(n)
            #     n.xForce= el.localForceVector[idx]
            #     n.yForce = el.localForceVector[idx+1]
        else:
            el.localForceVector = np.zeros(len(el.packageNodes())*el.BLnode.DOFsper)
        
        idx = 0
        for i in el.gaussPoints:
            shapeMat = buildShapeMatrix(i)
            derivShapeMat = buildShapeDerivMatrix(i)
            jacobian = derivShapeMat@nodalCoords
            bMat = quadBMatrix(jacobian, derivShapeMat)
            transformedCoords = shapeMat@nodalCoords
            
            tempStiff = (bMat.T @ self.elastConstMat() @ bMat)*el.gaussWeights[idx]*npl.det(jacobian)
            # TODO
            # CHECK THE LEADING TERMS OF THIS EXPRESSION
            
            # tempForce = (100*np.prod(transformedCoords)*shapeMat.T)*element.gaussWeights[idx]*npl.det(jacobian)
            el.localStiffMat = el.localStiffMat + tempStiff
            # element.localForceMat = element.localForceMat + tempForce
            idx += 1
        el.localStiffMat = el.localStiffMat.flatten()
        
    
    def globalAssembly(self):
        self.globalStiffnessMatrix = np.zeros([i*self.mesh.totalDOFs for i in [1, 1]])
        self.globalForceVector = np.zeros(self.mesh.totalDOFs)
        self.globalDisplacementVector = [None]*self.mesh.totalDOFs
        for el in list(itertools.chain(*self.mesh.elements)):
            self.localConstruction(el)
            
            if len(el.BC) > 0 and el.BC[0].kind == "constraint": #!!!!!!!!!!!! STUPID AND SHIT CAUSE IT ONLY LOOKS AT INDEX OF BC[0]!!!!!!!!!
                for n in el.packageNodes():
                    if n.xDisplacement != None:
                        self.globalDisplacementVector[n.xDOF-1] = el.BC[0].xMag
                    if n.yDisplacement != None:
                        self.globalDisplacementVector[n.yDOF-1] = el.BC[0].yMag
            idx = 0
            for globalDOF in el.packageDOFs():
                self.globalForceVector[globalDOF] += el.localForceVector[idx]
                idx += 1
                
                
            idx = 0
            for globalDOF in itertools.product(el.packageDOFs(), repeat=2):
                self.globalStiffnessMatrix[globalDOF] += el.localStiffMat[idx]
                idx += 1
                    
                
    # def packagePrescribedElements(self):
    #     effected = {}
    #     for BC in self.forces + self.constraints:
    #         effected = effected + effected.difference(set(BC.effectedElements))
    #     return(effected)
            
    # TODO
    # !!!!!!!!!!!MIGHT HAVE TO CONVERT FORCE TO TRACTION BY CONVERTING TO UNITS OF PASCALS!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!GENERATE TRANSVERSE TRACTIONS (SHEARS) BY ECCENTRIC OF FORCE AND EQUIV MOMENTS!!!!!!!!!!!
    # def applyForce(self, location, xMagnitude, yMagnitude, name=defaultForceName()):
    #     self.forces.append({"name": name, "location": location, "XMag": xMagnitude, "yMag": yMagnitude})
    #     elID = self.findClosestElement(location)
        
    #     xNormalizedLocation = location[0] - self.mesh.getElement(elID).BLnode.xCoord
    #     yNormalizedLocation = location[1] - self.mesh.getElement(elID).BLnode.yCoord
        
    #     xForceToTraction = xMagnitude/(self.mesh.getElement(elID).yLength * self.domain.depth())
    #     yForceToTraction = yMagnitude/(self.mesh.getElement(elID).xLength * self.domain.depth())
        
    #     leftEdgeMultiplier = xNormalizedLocation/self.mesh.getElement(elID).xLength
    #     rightEdgeMultiplier = 1 - leftEdgeMultiplier
    #     bottomEdgeMultiplier = yNormalizedLocation/self.mesh.getElement(elID).yLength
    #     topEdgeMultiplier = 1 - bottomEdgeMultiplier
        
    #     self.mesh.getElement(elID).leftEdgeTraction = np.array([0, xForceToTraction*leftEdgeMultiplier])
    #     self.mesh.getElement(elID).rightEdgeTraction = np.array([0, xForceToTraction*rightEdgeMultiplier])
    #     self.mesh.getElement(elID).bottomEdgeTraction = np.array([0, yForceToTraction*bottomEdgeMultiplier])
    #     self.mesh.getElement(elID).topEdgeTraction = np.array([0, yForceToTraction*topEdgeMultiplier])
        
        
    # def applyBC(self, bcType, location, xMagnitude, yMagnitude, name=defaultConstraintName()):
        
    #     self.BCs.append({"name": name, "location": location, "xMag": xMagnitude, "yMag": yMagnitude})
    #     elID = self.findClosestElement(location)
        
    #     xNormalizedLocation = location[0] - self.mesh.getElement(elID).BLnode.xCoord
    #     yNormalizedLocation = location[1] - self.mesh.getElement(elID).BLnode.yCoord

        
    # def findClosestElement(self, coords):
    #     currentMin = None
    #     for el in self.mesh.elements:
    #         diffNorm = npl.norm(coords - el.packageNodalCoords, ord="fro")
    #         if currentMin == None:
    #             currentMin = diffNorm
    #             closestElement = el.Id
    #         elif diffNorm < currentMin:
    #             closestElement = el.Id
    #     return closestElement
            
        
            
def test():
    setupObject = setup()
    setupObject.domain.setDomainParams(10, 10, 1, 2800, 70E9, .3)
    setupObject.mesh.configMesh(xFactor=5, yFactor=5, meshType="NpE")
    setupObject.mesh.generateMesh(setupObject.domain)
    boundaryCondition(setupObject, "force", "right", xMag=100)
    boundaryCondition(setupObject, "constraint", "left")
    setupObject.globalAssembly()
    return setupObject
      
if __name__ == "__main__":
    res = test()