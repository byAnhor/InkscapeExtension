#!/usr/bin/env python
import os
import sys
sys.path.append('C:\\Program Files\\Inkscape\\share\\inkscape\\extensions')
import math
import copy
import inkex
import svgwrite
from svgpathtools import *
#from simplepath import *

class SilhouetteExtension(inkex.EffectExtension):
    def init(self):
        inkex.Effect.init(self)

    def add_arguments(self, pars):
        pass

    def effect(self):
        savestdout = sys.stdout
        sys.stdout = sys.stderr
        with open('C:\\Temp\\silhouette.txt', 'w') as dbgfile:
            sys.stdout = dbgfile # Change the standard output to the file we created.
            svg = self.document.getroot()
            with open('C:\\Temp\\silhouette.xml', 'wb') as f:
                svg.getroottree().write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)
            svg2paths('C:\\Temp\\silhouette.xml')
            pathNodesList = self.document.xpath('//svg:path',namespaces=inkex.NSS)
            allbboxes = []
            for pathNode in pathNodesList:
                pathId = pathNode.attrib['id']
                pathD = pathNode.attrib['d']
                unitaryPath = parse_path(pathD)
                allPath = Path(unitaryPath)
                allbboxes.append(allPath[0].bbox())
            xmin = math.floor(min(allbboxes,key=lambda item:item[0])[0])
            xmax = math.ceil(max(allbboxes,key=lambda item:item[1])[1])
            ymin = math.floor(min(allbboxes,key=lambda item:item[2])[2])
            ymax = math.ceil(max(allbboxes,key=lambda item:item[3])[3])
        
            finalPathList = []
            simplifyExplodePathsList = []
            for pathNode in pathNodesList:
                pathId = pathNode.attrib['id']
                print("pathId %s"%(pathId))
                pathD = pathNode.attrib['d']
                unitaryPath = parse_path(pathD)
                for i,cur in enumerate(unitaryPath):
                    if isinstance(cur, Line):
                        unitaryPath[i] = CubicBezier(cur.start, cur.start, cur.end, cur.end)
                print("unitaryPath %s %s"%(type(unitaryPath), unitaryPath))
                explodePaths = unitaryPath.continuous_subpaths()  
                #print "explodePaths", type(explodePaths), explodePaths
                simplifyExplodePathsList.append(copy.deepcopy(explodePaths))
                for i,cur in reversed(list(enumerate(explodePaths))): 
                    if len(cur) == 2:
                        simplifyExplodePathsList[-1].pop(i)
                    elif len(cur) == 3:
                        cond = True
                        for j in range(0,2):
                            cb = cur[j]
                            rl = abs((cb.start-cb.end).real)
                            im = abs((cb.start-cb.end).imag)
                            cond = cond and cb.start==cb.control1 and cb.end==cb.control2 and rl<=1 and im <=1
                        if cond:
                            simplifyExplodePathsList[-1].pop(i)
                #print "simplifyExplodePathsList", type(simplifyExplodePathsList[-1]), len(simplifyExplodePathsList[-1]), simplifyExplodePathsList[-1]
                #print len(explodePaths), "=>", len(simplifyExplodePathsList[-1])
                print("simplifyExplodePathsList %s %s %s"%(type(simplifyExplodePathsList[-1]), len(simplifyExplodePathsList[-1]), simplifyExplodePathsList[-1]))
                #wsvg(paths=unitaryPath, filename='C:\\Temp\\layer%s_full.svg'%pathId)
                simplifyUnitaryPath = Path()
                for i,cur in enumerate(simplifyExplodePathsList[-1]):
                    for j,seg in enumerate(cur):
                        print("%s) %s) %s"%(i,j,seg))
                        simplifyUnitaryPath.append(seg)                
                #print "simplifyUnitaryPath", type(simplifyUnitaryPath), simplifyUnitaryPath
                finalPath = list()
                finalPath.append(simplifyUnitaryPath)
                finalPathList.append(simplifyUnitaryPath)
                finalPath.append(bbox2path(xmin, xmax, ymin, ymax))
                
                wsvg(paths=finalPath, filename='C:\\Temp\\layer%s_simplified.svg'%pathId)
                
            finalPathList.append(bbox2path(xmin, xmax, ymin, ymax))
            wsvg(paths=finalPathList, filename='C:\\Temp\\layerAll_simplified.svg')

        sys.stdout = savestdout
        
if __name__ == '__main__':
    SilhouetteExtension().run()
