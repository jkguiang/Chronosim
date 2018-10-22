import numpy as np
from stl import mesh
from outtree import OutTree
import ROOT
import os

def LoadMesh(stlDir, sf=1, verbose=False):
    """ Load polygon mesh, only return polygons with normal in z-direction """
    layers = []
    for i, stlFile in enumerate(os.listdir(stlDir)):
        lgadMesh = mesh.Mesh.from_file("{0}/{1}".format(stlDir, stlFile))
        allVectors = lgadMesh.vectors
        layers.append([])
        for j, n in enumerate(lgadMesh.normals):
            if (n[2] > 0):
                layers[i].append([ allVectors[j][0]*sf, allVectors[j][1]*sf, allVectors[j][2]*sf ])

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

    return layers

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

def CrossProduct(a, b):
    """ Return z-component of a x b """
    return (a[0]*b[1] - a[1]*b[0])

def CheckHit(poly, hitPos):
    """ Check that nearby ray's trajectory intersects polygon """
    hitPosToVertex = [[ (poly[0][0]-hitPos[0]), (poly[0][1]-hitPos[1]) ],
                      [ (poly[1][0]-hitPos[0]), (poly[1][1]-hitPos[1]) ], 
                      [ (poly[2][0]-hitPos[0]), (poly[2][1]-hitPos[1]) ]]

    z0 = CrossProduct(hitPosToVertex[0], hitPosToVertex[1])
    z1 = CrossProduct(hitPosToVertex[1], hitPosToVertex[2])
    z2 = CrossProduct(hitPosToVertex[2], hitPosToVertex[0])

    return (z0 > 0 and z1 > 0 and z2 > 0)


def Parse(stlDir, rayPath, outPath, verbose=False):
    """ Parse polygons and rays, look for hits """
    layers = LoadMesh(stlDir, sf=(0.001), verbose=verbose)
    rays = LoadRays(rayPath, verbose=verbose)
    outFile = ROOT.TFile(outPath, "RECREATE")
    rayOut = OutTree()
    # Loop over rays
    for i, ray in enumerate(rays):
        # Initialize output tree
        rayOut.GetKinematics(ray)
        nHits = 0
        layerHits = [ False for l in layers ]
        layerHitPosX = [ 0 for l in layers ]
        layerHitPosY = [ 0 for l in layers ]
        layerHitPosZ = [ 0 for l in layers ]
        # Loop over layers
        for j, layer in enumerate(layers):
            # Get particle's position at layer's z-level
            t = abs(layer[0][0][2] - ray["pos"][2])/ray["p"][2]
            hitPos = [ ray["pos"][0]+t*ray["p"][0], 
                       ray["pos"][1]+t*ray["p"][1],
                       ray["pos"][2]+t*ray["p"][2] ]
            # Save first position for all particles for efficiency calculation
            if j == 0:
                rayOut.x = hitPos[0]
                rayOut.y = hitPos[1]
                rayOut.z = hitPos[2]
            # Loop over polygons
            for poly in layer:
                # Calculate ray's proximity to first polygon vertex
                xDisp = abs(hitPos[0] - poly[0][0])
                yDisp = abs(hitPos[1] - poly[0][1])
                # Check for proximity then trajectory intersection
                if xDisp < 0.1 and yDisp < 0.1 and CheckHit(poly, hitPos):
                    nHits += 1
                    layerHits[j] = True
                    layerHitPosX[j] = hitPos[0]
                    layerHitPosY[j] = hitPos[1]
                    layerHitPosZ[j] = hitPos[2]

        # Set remaining branches
        rayOut.nHits = nHits
        rayOut.layerHits = np.array(layerHits)
        rayOut.layerHitPosX = np.array(layerHitPosX)
        rayOut.layerHitPosY = np.array(layerHitPosY)
        rayOut.layerHitPosZ = np.array(layerHitPosZ)
        # Fill tree
        rayOut.Fill()

    if verbose:
        print("Finished")

    rayOut.tree.Write()
    outFile.Close()

    return

if __name__ == "__main__":
    import sys
    stlDir = sys.argv[1]
    rayPath = sys.argv[2]
    outPath = sys.argv[3]
    Parse(stlDir, rayPath, outPath, verbose=False)
