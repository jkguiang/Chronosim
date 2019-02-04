import numpy as np
from stl import mesh
from outtree import OutTree
import ROOT
import os

from chronosim import LoadRays

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

def Sign(x):
    if x > 0: return 2
    elif x < 0: return 1
    else: return 0

def ParallelXY(a, b):
    return (Sign(a[0]) == Sign(b[0])) and (Sign(a[1]) == Sign(b[1]))

def CrossProduct(a, b):
    """ Return a x b """
    cross = []
    cross.append(a[1]*b[2] - a[2]*b[1])
    cross.append(a[2]*b[0] - a[0]*b[2])
    cross.append(a[0]*b[1] - a[1]*b[0])
    return cross


def GetTransform(v):
    # Original Coordinates
    A = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
    # New basis vectors in A-space
    e0 = [ 0, 0, 0 ]
    e1 = []
    e2 = A[2]
    # Get magnitude of input vector
    vMag = (v[0]**2+v[1]**2+v[2]**2)**0.5
    # Construct e0 along input vector
    for i in range(0,2):
        e0[i] = v[i]
    # e1 is simply e2 x e0
    e1 = CrossProduct(e2, e0)
    # Construct rotation matrix
    R = [ [e0[0], e1[0], e2[0]], 
          [e0[1], e1[1], e2[1]], 
          [e0[2], e1[2], e2[2]] ]

    return np.array(R)

def CheckHit(poly, hitPos, norm):
    """ Check that nearby ray's trajectory intersects polygon """
    hitPosToVertex = []
    # Get rotation matrix
    R = GetTransform(norm)
    for vertex in poly:
        # Get hit pos in rotated basis
        hitPosTransf = np.matmul(R, np.array(hitPos))
        vertexTransf = np.matmul(R, np.array(vertex))
        # Translate hit pos to polygon plane
        hitPosTransl = np.add(hitPosTransf, np.array([vertexTransf[0]-hitPosTransf[0],0,0]))
        # Store vector between hit pos and vertex
        hitPosToVertex.append([ vertexTransf[0]-hitPosTransl[0], 
                                vertexTransf[1]-hitPosTransl[1],
                                vertexTransf[2]-hitPosTransl[2] ])

    # Take cross products
    cross0 = CrossProduct(hitPosToVertex[0], hitPosToVertex[1])
    cross1 = CrossProduct(hitPosToVertex[1], hitPosToVertex[2])
    cross2 = CrossProduct(hitPosToVertex[2], hitPosToVertex[0])
    # Get norm in rotate basis
    normTransf = np.matmul(R, np.array(norm))

    return (ParallelXY(cross0, normTransf) and ParallelXY(cross1, normTransf) and ParallelXY(cross2, normTransf)) 

def Parse(stlDir, rayPath, outPath, verbose=False):
    """ Parse polygons and rays, look for hits """
    layers, norms = LoadMesh(stlDir, sf=(0.001), verbose=verbose)
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
