# -*- coding: utf-8 -*-
import numpy as np
from stl import mesh
from outtree import OutTree
import ROOT
import os

def DotProduct(a, b):
    """ Return a·b """
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def CrossProduct(a, b):
    """ Return a x b """
    return [ (a[1]*b[2] - a[2]*b[1]), (a[2]*b[0] - a[0]*b[2]), (a[0]*b[1] - a[1]*b[0]) ]

def GetTransform(n):
    """ Get matrix R that rotates point into new basis
        where z -> n (normalized facet normal vector)
    """
    # New basis vectors in original coordinates
    e3 = n
    if n[2] != 0:
        e2 = [0,1,0]              
    else:
        e2 = [0,0,1]
    e1 = CrossProduct(e2, e3)
    # Construct rotation matrix
    R = [ [e1[0], e1[1], e1[2]], 
          [e2[0], e2[1], e2[2]], 
          [e3[0], e3[1], e3[2]] ]

    return R

def CheckHit(poly, hitPos, norm):
    """ Check that nearby ray's trajectory intersects polygon """
    # Return False if hit pos on opposite side of BTL
    if DotProduct(hitPos, norm) < 0:
        return False
    # Stores vectors from hit pos to each vertex of poly
    hitPosToVertex = []
    # Get rotation matrix
    R = GetTransform(norm)
    for vertex in poly:
        # Get hit pos and vertex in rotated basis
        hitPosTransf = np.matmul(R, hitPos)
        vertexTransf = np.matmul(R, vertex)
        # Translate hit pos and vertex to same plane
        hitPosTransf[2] = 0
        vertexTransf[2] = 0
        # Store vector between hit pos and vertex
        hitPosToVertex.append(np.subtract(vertexTransf, hitPosTransf))

    # Take cross products
    cross0 = CrossProduct(hitPosToVertex[0], hitPosToVertex[1])
    cross1 = CrossProduct(hitPosToVertex[1], hitPosToVertex[2])
    cross2 = CrossProduct(hitPosToVertex[2], hitPosToVertex[0])

    return (cross0[2] > 0 and cross1[2] > 0 and cross2[2] > 0)

def Parse(layers, norms, rays, outPath, verbose=False):
    """ Parse polygons and rays, look for hits """
    # Setup output file
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
        # Get (potential) hit position
        hitPos = ray["pos"]
        # Loop over layers
        for j, layer in enumerate(layers):
            # Save first position for all particles for efficiency calculation
            if j == 0:
                rayOut.x = hitPos[0]
                rayOut.y = hitPos[1]
                rayOut.z = hitPos[2]
            # Loop over polygons
            for k, poly in enumerate(layer):
                # Check for proximity then trajectory intersection
                if CheckHit(poly, hitPos, norms[j][k]):
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
        print("{} hits".format(nHits))
        print("Finished")

    rayOut.tree.Write()
    outFile.Close()

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
        Parse(stlDir, rayPath, outPath, verbose=True)
