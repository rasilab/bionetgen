# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:44:17 2012

@author: proto
"""
from copy import deepcopy
class Species:
    def __init__(self):
        self.molecules = []
        
    def addMolecule(self,molecule,concatenate=False,iteration = 1):
        if not concatenate:
            self.molecules.append(molecule)
        else:
            counter = 1
            for element in self.molecules:
                if element.name == molecule.name:
                    element.extend(molecule)
            #self.molecules.append(molecule)
            #for element in self.molecules:
            #    if element.name == molecule.name:
        
    def getMolecule(self,moleculeName):
        for molecule in self.molecules:
            if moleculeName == molecule.name:
                return molecule
        return None
    def getSize(self):
        return len(self.molecules)
        
    def getMoleculeNames(self):
        return [x.name for x in self.molecules]
    
    def contains(self,moleculeName):
        for molecule in self.molecules:
            if moleculeName == molecule.name:
                return True
        return False
        
    def addChunk(self,tags,moleculesComponents,precursors):
        '''
        temporary transitional method
        '''
        for (tag,components) in zip (tags,moleculesComponents):
            if self.contains(tag):
                tmp = self.getMolecule(tag)
            else:
                tmp = Molecule(tag)
                #for element in precursors:
                #    if element.getMolecule(tag) != None:
                #        tmp = element.getMolecule(tag)
            
            for component in components:
                if tmp.contains(component[0][0]):
                    tmpCompo = tmp.getComponent(component[0][0])
                    #continue
                else:
                    tmpCompo = Component(component[0][0])
                
                for index in range(1,len(component[0])):
                    tmpCompo.addState(component[0][index])
                if len(component) > 1:
                    tmpCompo.addBond(component[1])
                if not tmp.contains(component[0][0]):   
                    tmp.addComponent(tmpCompo)
            if not self.contains(tag):
                self.molecules.append(tmp)
                
    def extend(self,species):
        if(len(self.molecules) == len(species.molecules)):
            for (selement,oelement) in zip(self.molecules,species.molecules):
                for component in oelement.components:
                    if component.name not in [x.name for x in selement.components]:
                        selement.components.append(component)
                    else:
                        for element in selement.components:
                            if element.name == component.name:
                                element.states.append(component.states)
        else:
            for element in species.molecules:
                #pass
                if element.name not in [x.name for x in self.molecules]:
                    #print 'kkkkkkkkkkkkk',str(element),str(self)
                    self.addMolecule(deepcopy(element))
                else:
                    for molecule in self.molecules:
                        if molecule.name == element.name:
                            for component in element.components:
                                if component.name not in [x.name for x in molecule.components]:
                                    molecule.addComponent(deepcopy(component))
                    
    
    def append(self,species):
        for element in species.molecules:
            self.molecules.append(deepcopy(element))              
        
    def __str__(self):
        return '.'.join([x.toString() for x in self.molecules])
        
    def toString(self):
        return self.__str__()
        

class Molecule:
    def __init__(self,name):
        self.components = []
        self.name = name
        
    def addChunk(self,chunk):
        component = Component(chunk[0][0][0][0])
        component.addState(chunk[0][0][0][1])
        self.addComponent(component)
        
    def addComponent(self,component):
        self.components.append(component)
        
    def getComponent(self,componentName):
        for component in self.components:
            if componentName == component.getName():
                return component
                
    def removeComponent(self,componentName):
        x = [x for x in self.components if x.name == componentName]
        if x != []:
            self.components.remove(x[0])
            
    def removeComponents(self,components):
        for element in components:
            if element in self.components:
                self.components.remove(element)
                
    def addBond(self,componentName,bondName):
        component = self.getComponent(componentName)
        component.addBond(bondName)
        
    def getComponentWithBonds(self):
        return [x.name for x in self.components if x.bonds != []]
        
    def contains(self,componentName):
        return componentName in [x.name for x in self.components]
        
    def __str__(self):
        self.components.sort()
        return self.name + '(' + ','.join([str(x) for x in self.components]) + ')'
        
    def toString(self):
        return self.__str__()
        
    def extend(self,molecule):
        for element in molecule.components:
            comp = [x for x in self.components if x.name == element.name]
            if len(comp) == 0:
                self.components.append(deepcopy(element))
            else:
                for bond in element.bonds:
                    comp[0].addBond(bond)
    
class Component:
    def __init__(self,name,bonds = [],states=[]):
        self.name = name
        self.states = states
        self.bonds = []
        self.activeState = ''
        
    def addState(self,state):
        self.states.append(state)
        self.setActiveState(state)
        
    def addBond(self,bondName):
        if not bondName in self.bonds:
            self.bonds.append(bondName)
        
    def setActiveState(self,state):
        if state not in self.states:
            return False
        self.activeState = state
        return True
        
    def getRuleStr(self):
        tmp = self.name
        if len(self.bonds) > 0:
            tmp += '!' + '!'.join([str(x) for x in self.bonds])
        if self.activeState != '':
            tmp += '~' + self.activeState
        return tmp
        
    def getTotalStr(self):
        return self.name + '~'.join(self.states)
    
    def getName(self):
        return self.name 
        
    def __str__(self):
        return self.getRuleStr()
        
    def __hash__(self):
        return self.name
        
        
class Databases:
    def __init__(self):
        self.translator ={}
        self.synthesisDatabase = {}
        self.catalysisDatabase = {}
        self.rawDatabase = {}
        self.labelDictionary = {}
        self.synthesisDatabase2 = {}
        
    def getRawDatabase(self):
        return self.rawDatabase
        
    def getLabelDictionary(self):
        return self.labelDictionary
        
    def add2LabelDictionary(self,key,value):
        temp = tuple(key)
        temp = temp.sort()
        self.labelDictionary[temp] = value

    def add2RawDatabase(self,rawDatabase):
        pass
    
    def getTranslator(self):
        return self.translator
    