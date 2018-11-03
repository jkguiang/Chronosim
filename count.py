import numpy as np
from tqdm import tqdm
from chronosim import LoadMesh

class Output:
    def __init__(self):
        self.out = {}

    def AddLayer(self, layer):
        self.out[layer] = {}

    def AddRect(self, layer, index, vert):
        self.out[layer][index] = { "pos":[vert[0], vert[1], vert[2]],
                                   "above": [],
                                   "below": [] }

def FirstPass(output, layer, index, poly1, poly2):
    """ Organize STL polygons into basic output form """
    sameVert = 0
    for vert1 in poly1:
        if sameVert == 2: break
        for vert2 in poly2:
            if np.array_equal(vert2, vert1):
                sameVert += 1

    if sameVert == 2:
        output.AddRect(layer, index, poly1[0])
        return True

    else:
        return False

def SecondPass(layers, resp1, verbose=False):
    """ Associate all vertically-inline LGADs with one another """
    return

def Parse(layers, NthPass, verbose=False):
    """ Parse STL polygons """
    output = Output()
    good = 0
    bad = 0
    for i, layer in enumerate(layers):
        output.AddLayer(i)
        for j, poly in enumerate(layer):
            if j != len(layer)-1 and j%2 == 0:
                poly1 = layer[j]
                poly2 = layer[j+1]
                result = NthPass(output, i, j, poly1, poly2)
                if result:
                    good += 1
                else:
                    bad += 1

    return output

def Count(stlDir, verbose=False):
    # Load Layers
    layers = LoadMesh(stlDir, sf=(0.001), verbose=verbose)
    Parse(layers, FirstPass, verbose=verbose)
    return

if __name__ == "__main__":
    stlDir = "/nfs-7/userdata/jguiang/chronosim/stl/inline-2x2_41mmGap"
    Count(stlDir, verbose=True)
