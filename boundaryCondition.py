# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:43:02 2020

@author: mns72
"""
import feaErrors
import numpy as np

def defaultForceName():
    if "forceCount" not in globals():
        global forceCount
        forceCount = 0
    forceCount += 1
    forceName = "Force" + str(forceCount)
    return forceName

def defaultConstraintName():
    if "conCount" not in globals():
        global conCount
        conCount = 0
    conCount += 1
    conName = "Constraint" + str(conCount)
    return conName


class boundaryCondition():
            
    def __init__(self, setupObject, kind, edgeID, span=None, xMag=0, yMag=0, name=None):
        self.edgeID = edgeID
        self.xMag = xMag
        self.yMag = yMag
        self.effectedElements = getattr(setupObject.mesh, edgeID + "Boundary")
        self.kind = kind
        
        if kind == "force":
            self.traction = self.setTraction()
            if name == None:
                self.name = defaultForceName()
            setupObject.forces.append(self)
        elif kind == "constraint":
            self.setNodalDisplacements()
            if name == None:
                self.name = defaultConstraintName()
            setupObject.constraints.append(self)
        elif kind != "force" or kind != "constraint":
            raise(feaErrors.InvalidbcTypeError("The passed BC type is invalid!"))
        
    
        # self.effectedElements = self.getEffectedElements(setupObject.mesh, span, edgeID)

        
    
    # TODO
    # !!!!!!!!!COME UP WITH A BETTER SCHEME FOR ASSIGNING WHAT NODES ARE "CONTAINED" IN A SPAN!!!!!!!!!!!!    
    # def getEffectedElements(self, mesh, span, edgeID):
    #     edgeName = edgeID + "Boundary"
    #     effected = []
    #     for element in getattr(mesh, edgeName):
    #         if (edgeID == "bottom" or edgeID == "top") and (element.BLnode.xCoord > span[0] or element.BRnode.xCoord < span[1]):
    #             effected.append(element)
    #         elif (edgeID == "left" or edgeID == "right") and (element.BLnode.yCoord > span[0] or element.TLnode < span[1]):
    #             effected.append(element)
    #         else:
    #             raise(ValueError("Invalid edgeID or boundary condition span is outside of domain!"))
    #         element.BC.append(self)
    #     return effected
    
    def setTraction(self):
        if self.edgeID == "top":
            stressMat = np.array([[0, self.yMag], [self.yMag, self.xMag]])
            edgeNormal = np.array([0, 1])
        elif self.edgeID == "bottom":
            stressMat = np.array([[0, self.yMag], [self.yMag, self.xMag]])
            edgeNormal = np.array([0, -1])
        elif self.edgeID == "right":
            stressMat = np.array([[self.xMag, self.yMag], [self.yMag, 0]])
            edgeNormal = np.array([1, 0])
        elif self.edgeID == "left":
            stressMat = np.array([[self.xMag, self.yMag], [self.yMag, 0]])
            edgeNormal = np.array([-1, 0])
            
        for el in self.effectedElements:
            el.BC.append(self)
            el.traction = (stressMat @ edgeNormal.T)/len(self.effectedElements)

        return stressMat @ edgeNormal.T
    
    def setNodalDisplacements(self):
        if self.edgeID == "top":
            nodeIds = ["TLnode", "TRnode"]
        elif self.edgeID == "bottom":
            nodeIds = ["BLnode", "BRnode"]
        elif self.edgeID == "right":
            nodeIds = ["BRnode", "TRnode"]
        elif self.edgeID == "left":
            nodeIds = ["TLnode", "BLnode"]
        
        for el in self.effectedElements:
            el.BC.append(self)
            for i in nodeIds:
                getattr(el, i).xDisplacement = self.xMag
                getattr(el, i).yDisplacement = self.yMag
                
    
        
        
        