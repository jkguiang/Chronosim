import ROOT
import numpy as np

class OutTree:
    def __init__(self):
        self.tree = ROOT.TTree("Events","")
        
        self.pdgID = 0.
        self.q = 0.
        self.m = 0.
        self.x = 0.
        self.y = 0.
        self.z = 0.
        self.angle = 0.
        self.px = 0.
        self.py = 0.
        self.pz = 0.
        self.pt = 0.
        self.eta = 0.
        self.phi = 0.
        self.nHits = 0.
        self.layerHits = np.zeros(4, dtype=bool)
        self.layerHitPosX = np.zeros(4, dtype=float)
        self.layerHitPosY = np.zeros(4, dtype=float)
        self.layerHitPosZ = np.zeros(4, dtype=float)

        self._pdgID = np.zeros(1, dtype=float)
        self._q = np.zeros(1, dtype=float)
        self._m = np.zeros(1, dtype=float)
        self._x = np.zeros(1, dtype=float)
        self._y = np.zeros(1, dtype=float)
        self._z = np.zeros(1, dtype=float)
        self._angle = np.zeros(1, dtype=float)
        self._px = np.zeros(1, dtype=float)
        self._py = np.zeros(1, dtype=float)
        self._pz = np.zeros(1, dtype=float)
        self._pt = np.zeros(1, dtype=float)
        self._eta = np.zeros(1, dtype=float)
        self._phi = np.zeros(1, dtype=float)
        self._nHits = np.zeros(1, dtype=float)
        self._layerHits = np.zeros(4, dtype=bool)
        self._layerHitPosX = np.zeros(4, dtype=float)
        self._layerHitPosY = np.zeros(4, dtype=float)
        self._layerHitPosZ = np.zeros(4, dtype=float)

        self.tree.Branch("pdgID",self._pdgID,"pdgID/D")
        self.tree.Branch("q",self._q,"q/D")
        self.tree.Branch("m",self._m,"m/D")
        self.tree.Branch("x",self._x,"x/D")
        self.tree.Branch("y",self._y,"y/D")
        self.tree.Branch("z",self._z,"z/D")
        self.tree.Branch("angle",self._angle,"angle/D")
        self.tree.Branch("px",self._px,"px/D")
        self.tree.Branch("py",self._py,"py/D")
        self.tree.Branch("pz",self._pz,"pz/D")
        self.tree.Branch("pt",self._pt,"pt/D")
        self.tree.Branch("eta",self._eta,"eta/D")
        self.tree.Branch("phi",self._phi,"phi/D")
        self.tree.Branch("nHits",self._nHits,"nHits/D")
        self.tree.Branch("layerHits",self._layerHits,"layerHits[4]/O")
        self.tree.Branch("layerHitPosX",self._layerHitPosX,"layerHitPosX[4]/D")
        self.tree.Branch("layerHitPosY",self._layerHitPosY,"layerHitPosY[4]/D")
        self.tree.Branch("layerHitPosZ",self._layerHitPosZ,"layerHitPosZ[4]/D")

    def Fill(self):
        
        self._pdgID[0] = self.pdgID
        self._q[0] = self.q
        self._m[0] = self.m
        self._x[0] = self.x
        self._y[0] = self.y
        self._z[0] = self.z
        self._angle[0] = self.angle
        self._px[0] = self.px
        self._py[0] = self.py
        self._pz[0] = self.pz
        self._eta[0] = self.eta
        self._phi[0] = self.phi
        self._nHits[0] = self.nHits
        for l, val in enumerate(self.layerHits):
            self._layerHits[l] = val
        for i, x in enumerate(self.layerHitPosX):
            self._layerHitPosX[i] = x
        for j, y in enumerate(self.layerHitPosY):
            self._layerHitPosY[j] = y
        for k, z in enumerate(self.layerHitPosZ):
            self._layerHitPosZ[k] = z

        self.tree.Fill()

    def GetKinematics(self, rayObj):
        self.pdgID = rayObj["id"]
        self.q = rayObj["charge"]
        self.m = rayObj["mass"]
        self.angle = np.arctan(rayObj["p"][2]/(rayObj["p"][0]**2 + rayObj["p"][1]**2)**(2))
        self.px = rayObj["p"][0]
        self.py = rayObj["p"][1]
        self.pz = rayObj["p"][2]
        self.pt = rayObj["pt"]
        self.eta = rayObj["eta"]
        self.phi = rayObj["phi"]
