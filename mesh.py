# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:25:35 2020

@author: mns72
"""
import feaErrors
import numpy as np
from element import element
from collections import Counter
from node import node
import itertools

# TODO
# USE GRAVITY

def setBoundaryIDs(boundaryElements, boundaryId):
    for el in boundaryElements:
        el.boundaryID = boundaryId

class mesh():
    
    def __init__(self):
        self.elements = []
        self.numOfNodes = None
        self.numOfEls = None
        self.totalDOFs = None
        self.meshConfig = {}
        self.nodesPerEl = 4
        self.conMatrix = []
        self.boundary = []
        self.bottomBoundary  = []
        self.rightBoundary = []
        self.topBoundary = []
        self.leftBoundary = []
        self.elementalMass = None
        self.nodeDict = {}
        
    def checkConfig(self):
        if self.meshConfig["meshType"] != "asPerc" and self.meshConfig["meshType"] != "NpE":
            raise feaErrors.InvalidMeshConfig("Entered invalid mesh type!")  
        
        elif self.meshConfig["meshType"] == "asPerc" and (self.meshConfig["xFactor"] >= 1 or self.meshConfig["yFactor"] >=1):
            raise feaErrors.InvalidMeshConfig("meshType is configured as 'as percentage' but xfactor or yfactor are greater than 100 percent")
        
        elif self.meshConfig["meshType"] == "NpE" and (not isinstance(self.meshConfig["xFactor"], int)) or (not isinstance(self.meshConfig["yFactor"], int)):
            raise feaErrors.InvalidMeshConfig("meshType is configured as 'nodes per edge' but xFactor or yFactor are not integers")
            
        elif len(self.meshConfig) == 0:
            raise feaErrors.InvalidMeshConfig("You can not generate the mesh before configuring the mesh!")
    
      
    def configMesh(self, xFactor=0.05, yFactor=0.05, meshType="asPerc"):
        '''
        Sets the config params for a mesh object.
        
        Parameters
        ----------
        meshDictionary:
            meshType: string {default: asPerc, alternative: NpE}
                asPerc defines edge node count using xFactor and yFactor 
                as a length percentage of the domain x and y dimensions.
                
                NpE defines edge node count using xFactor and yFactor as 
                the number of nodes per edge.
                
            xFactor: number
                Constant used to define x direction node count. 
                If using "asPer", pass xFactor as a percentage in decimal form.
                If using "NpE", pass xFactor as an integer.
                
            yFactor: number
                Constant used to define y direction node count. 
                If using "asPer", pass yFactor as a percentage in decimal form.
                If using "NpE", pass yFactor as an integer.

        '''
        self.meshConfig = {"meshType": meshType, "xFactor": xFactor, "yFactor": yFactor}
        self.checkConfig()
        
    
    def getElement(self, elementId):
        for el in list(itertools.chain(*self.elements)):
            if el.Id == elementId:
                return el
        raise(ValueError("The passed element ID is out of the mesh bounds!"))
        
    def buildConnectMat(self):
        for i in range(1, self.numOfEls + 1):
            self.conMatrix.append(np.array(self.getElement(i).packageNodeIds()))
        self.conMatrix = np.array(self.conMatrix)
        
            
    def generateElements(self, domain):
        tempRow = []
        xLength = domain.length/self.numOfXElems
        yLength = domain.height/self.numOfYElems
        self.elementalMass = xLength*yLength*domain.depth*domain.density
        rowIdx = self.numOfYElems - 1
        colIdx = self.numOfXElems - 1
        for i in range(1, self.numOfEls + 1):
            tempRow.append(element(self.numOfEls + 1 - i, [rowIdx, colIdx], xLength, yLength))
            colIdx -= 1
            if i%self.numOfXElems == 0:
                self.elements.append(tempRow[::-1])
                rowIdx -= 1
                colIdx = self.numOfXElems - 1
                tempRow = []
            
                
    def assignElementValues(self):
        for el in list(itertools.chain(*self.elements)):
            el.setLocalNodes(self.numOfXElems, self.numOfYElems)
            el.setGauss()
    
    def extractBoundaryElements(self):
        self.bottomBoundary = self.elements[0]
        setBoundaryIDs(self.bottomBoundary, "bottom")
        self.topBoundary = self.elements[-1]
        setBoundaryIDs(self.topBoundary, "top")
        for i in range(self.numOfYElems):
            self.leftBoundary.append(self.elements[i][0])
            self.rightBoundary.append(self.elements[i][-1])
        setBoundaryIDs(self.leftBoundary, "left")
        setBoundaryIDs(self.rightBoundary, "right")
        self.boundary = list(set(self.bottomBoundary + self.rightBoundary + self.topBoundary + self.leftBoundary))
        
    def nodeDofDictionary(self):
        for el in list(itertools.chain(*self.elements)):
            for n in el.packageNodes():
                self.nodeDict[n.xDOF] = n
                self.nodeDict[n.yDOF] = n
            
        

    def generateMesh(self, domain):
        if self.meshConfig["meshType"] == "asPerc":
            None
        elif self.meshConfig["meshType"] == "NpE":
            self.numOfXElems = self.meshConfig["xFactor"]
            self.numOfYElems = self.meshConfig["yFactor"]
        
        self.numOfEls = self.numOfXElems*self.numOfYElems
        self.numOfNodes = (self.numOfXElems + 1) * (self.numOfYElems + 1)
        self.totalDOFs = self.numOfNodes*2 # CHECK CHECK CHECK    
        self.generateElements(domain)   
        self.assignElementValues()
        self.buildConnectMat()
        self.extractBoundaryElements()
    
                
        
        
        
            
        
            