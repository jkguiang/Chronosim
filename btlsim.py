# -*- coding: utf-8 -*-
from stl import mesh
import os
from chronosim import Parse

def LoadMesh(stlDir, sf=1, verbose=False, rCut=1168, aCut=400000):
    """ Load polygon mesh, only return polygons at BTL radius """
    layers = []
    norms = []
    for i, stlFile in enumerate(sorted(os.listdir(stlDir))):
        lgadMesh = mesh.Mesh.from_file("{0}/{1}".format(stlDir, stlFile))
        allVectors = lgadMesh.vectors
        layers.append([])
        norms.append([])
        for j, n in enumerate(lgadMesh.normals):
            v = allVectors[j][0]
            # Calculate radius
            r = int((v[0]**2 + v[1]**2)**0.5)
            if r == rCut and n[2] == 0:
                # Calculate area
                a = (n[0]**2+n[1]**2+n[2]**2)**0.5
                if 0.5*a > aCut:
                    layers[i].append([ allVectors[j][0]*sf, allVectors[j][1]*sf, allVectors[j][2]*sf ])
                    norms[i].append([n[0]/a, n[1]/a, n[2]/a])

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
        Run(stlDir, rayPath, outPath, verbose=True)
