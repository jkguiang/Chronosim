# -*- coding: utf-8 -*-
from stl import mesh
import os
from chronosim import Parse

def LoadMesh(stlDir, sf=1, verbose=False):
    """ Load polygon mesh, only return polygons with normal in z-direction """
    layers = []
    for i, stlFile in enumerate(sorted(os.listdir(stlDir))):
        lgadMesh = mesh.Mesh.from_file("{0}/{1}".format(stlDir, stlFile))
        allVectors = lgadMesh.vectors
        layers.append([])
        for j, n in enumerate(lgadMesh.normals):
            if (n[2] > 0):
                # Calculate area
                a = (n[0]**2+n[1]**2+n[2]**2)**0.5
                layers[i].append([ allVectors[j][0]*sf, allVectors[j][1]*sf, allVectors[j][2]*sf ])
                norms[i].append([n[0]/a, n[1]/a, n[2]/a])

    if verbose:
        print("Loaded polygons from directory: {}".format(stlDir))
        nLGAD = 0 
        for k, layer in enumerate(layers):
            print("{0} LGADs in layer {1}".format(len(layer)/2, k))
            nLGAD += len(layer)/2
        nASIC = nLGAD*2
        print("---------------- Cost ----------------")
        print("+ {0} LGADs (${1})".format(nLGAD, 140*nLGAD))
        print("+ {0} ASICs (${1})".format(nASIC, 51*nASIC))
        print("+ {0} Al-N Support Structures (${1})".format(nASIC, 2*nASIC))
        print("+ {0} Power Converters (${1})".format(nASIC, 3*nASIC))
        print("+ {0} Transceivers (${1})".format(nASIC, 4*nASIC))
        print("______________________________________")
        print("= ${} total".format(140*nLGAD+60*nASIC))

    return layers, norms

def LoadRays(rayPath, verbose=False):
    """ Load ray trajectory data from txt file, map to dict """
    rays = []
    with open(rayPath, "r") as rayFile:
        for line in rayFile.readlines():
            ray = [ float(val) for val in line.split() ]
            rays.append({ "id":     ray[0],
                          "mass":   ray[1],
                          "charge": ray[2],
                          "pt":     ray[3],
                          "eta":    ray[4],
                          "phi":    ray[5],
                          "pos":    [ ray[6], ray[7], ray[8] ],
                          "p":    [ ray[9], ray[10], ray[11] ]}) 
    if verbose:
        print("Loaded {0} trajectories from file {1}".format(len(rays), rayPath))

    return rays

def Run(stlDir, rayPath, outPath, verbose=True):
    """ Load data and run simulation """
    # Load layers and normal vectors
    layers, norms = LoadMesh(stlDir, sf=(0.001), verbose=verbose)
    # Load rays
    rays = LoadRays(rayPath, verbose=verbose)
    # Run simulation
    Parse(layers, norms, rays, outPath, verbose=verbose)

    return

if __name__ == "__main__":
    import sys
    if sys.argv[2] == "-debug":
        stlDir = sys.argv[1]
        LoadMesh(stlDir, sf=(0.001), verbose=True)
    else:
        stlDir = sys.argv[1]
        rayPath = sys.argv[2]
        outPath = sys.argv[3]
        Parse(stlDir, rayPath, outPath, verbose=False)
