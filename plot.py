import ROOT
import os
from subprocess import call

class ChronoPlots:
    def __init__(self, inPath="", outDir="", 
                       endcapOuterRad=1.27, endcapInnerRad=0.315):
        self.tChain = ROOT.TChain("Events")
        self.outDir = outDir 
        self.LoadFile(inPath)
        self.endcapOuterRad = endcapOuterRad
        self.endcapInnerRad = endcapInnerRad

    def LoadFile(self, inPath):
        if inPath.split(".")[-1] == "root" and os.path.isfile(inPath):
            self.tChain.Add(inPath)
        return

    def OverallEff(self, nLayer):
        if nLayer >= 3:
            print("Please enter a layer below layer 3.")
            return
        # Load Weights
        ROOT.gROOT.ProcessLine(".L GetWeight.h")
        # Setup canvas
        c = ROOT.TCanvas("c", "c", 400, 400) 
        # nHits = self.tChain.GetEntries("pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1} && (layerHits[{2}] == 1 || layerHits[{3}] == 1)".format(self.endcapOuterRad, self.endcapInnerRad, nLayer, nLayer+1))
        # nAll = self.tChain.GetEntries("pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1}".format(self.endcapOuterRad, self.endcapInnerRad))
        # return round(float(nHits)/float(nAll), 2)
        # Number of Hits
        nHits = ROOT.TH1D("nHits", "", 1, 0, 2)
        nHitsSelect = "(pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1} && (layerHits[{2}] == 1 || layerHits[{3}] == 1))*GetWeight(eta)".format(self.endcapOuterRad, self.endcapInnerRad, nLayer, nLayer+1)
        self.tChain.Draw("1 >> nHits", nHitsSelect, "")
        # All hits
        nAll = ROOT.TH1D("nAll", "", 1, 0, 2)
        nAllSelect = "(pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1})*GetWeight(eta)".format(self.endcapOuterRad, self.endcapInnerRad)
        self.tChain.Draw("1 >> nAll", nAllSelect, "")
        # Divide
        nHits.Divide(nAll)
        nHits.Draw()

        return round(nHits.GetBinContent(1), 3)

    def TwoDiskOverallEff(self):
        nHits = self.tChain.GetEntries("pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1} && ((layerHits[0]==1 || layerHits[1]==1) && (layerHits[2]==1 || layerHits[3]==1))".format(self.endcapOuterRad, self.endcapInnerRad))
        nAll = self.tChain.GetEntries("pt > 0.5 && pow(x*x+y*y, 0.5) < {0} && pow(x*x+y*y, 0.5) > {1}".format(self.endcapOuterRad, self.endcapInnerRad))
        return round(float(nHits)/float(nAll), 2)

    def LayerHits(self, nLayer):
        if nLayer > 3:
            print("Please enter the index of an existing layer.")
            return
        # Setup canvas
        c0 = ROOT.TCanvas("c0", "c0", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)
        nLayer = str(nLayer)

        # Layer hits
        layerPlot = ROOT.TH2D("layerhits"+nLayer, "Layer {} Hits".format(nLayer), 520,-1.30,1.30,520,-1.30,1.30)
        self.tChain.Draw("layerHitPosY["+nLayer+"]:layerHitPosX["+nLayer+"]>>layerhits"+nLayer,
                         "layerHits["+nLayer+"]==1", "colz")

        c0.SaveAs("{0}/{1}.pdf".format(self.outDir, "LayerHits"+nLayer))

    def TwoLayerHits(self, nLayer):
        if nLayer >= 3:
            print("Please enter a layer below layer 3.")
            return
        # Setup canvas
        c1 = ROOT.TCanvas("c1", "c1", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)
        nLayer1 = str(nLayer)
        nLayer2 = str(nLayer+1)
        plotID = nLayer1+nLayer2

        # Layer hits
        twoLayerPlot = ROOT.TH2D("layerhits"+plotID, "Layer {0} OR {1} Hits".format(nLayer1, nLayer2), 520,-1.30,1.30,520,-1.3,1.3)
        self.tChain.Draw("y:x>>layerhits"+plotID,
                         "layerHits["+nLayer1+"]==1 || layerHits["+nLayer2+"]==1", "colz")

        c1.SaveAs("{0}/{1}.pdf".format(self.outDir, "LayerHits"+plotID))
        return

    def LayerHitEff(self, nLayer):
        if nLayer >= 3:
            print("Please enter a layer below layer 3.")
            return
        # Setup canvas
        c2 = ROOT.TCanvas("c2", "c2", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)
        nLayer1 = str(nLayer)
        nLayer2 = str(nLayer+1)
        plotID = nLayer1+nLayer2

        # Layer hits
        hitPosPlot = ROOT.TH2D("hitpos"+plotID, "Layer {0} OR {1} Hit Efficiency".format(nLayer1, nLayer2), 520,-1.30,1.30,520,-1.3,1.3)
        self.tChain.Draw("y:x>>hitpos"+plotID,
                         "layerHits["+nLayer1+"]==1 || layerHits["+nLayer2+"]==1", "colz")
        # Fill edges of disk so that they show up in plot
        for xBin in range(1, hitPosPlot.GetNbinsX()+1):
            for yBin in range(1, hitPosPlot.GetNbinsY()+1):
                val = hitPosPlot.GetBinContent(xBin,yBin)
                x = abs(hitPosPlot.GetXaxis().GetBinCenter(xBin))
                y = abs(hitPosPlot.GetYaxis().GetBinCenter(yBin))
                if val == 0 and x < self.endcapOuterRad and y < self.endcapOuterRad:
                    yMax = (self.endcapOuterRad**(2)-x**(2))**(0.5)
                    xMax = (self.endcapOuterRad**(2)-y**(2))**(0.5)
                    if x <= self.endcapInnerRad:
                        yMin = (self.endcapInnerRad**(2)-x**(2))**(0.5)
                    else:
                        yMin = -yMax
                    if y <= self.endcapInnerRad:
                        xMin = (self.endcapInnerRad**(2)-y**(2))**(0.5)
                    else:
                        xMin = -xMax
                    if xMin < x and x < xMax and yMin < y and y < yMax:
                        hitPosPlot.SetBinContent(xBin, yBin,0.01)
        # Layer hits
        allPosPlot = ROOT.TH2D("allpos"+plotID, "Layer {0} OR {1} Hit Efficiency".format(nLayer1, nLayer2), 520,-1.30,1.30,520,-1.3,1.3)
        self.tChain.Draw("y:x>>allpos"+plotID, "", "colz")
        # Divide hit positions by all positions
        hitPosPlot.Divide(allPosPlot)
        hitPosPlot.Draw("colz")
        # Plot settings
        hitPosPlot.GetYaxis().SetTitle("y (meters)")
        hitPosPlot.GetXaxis().SetTitle("x (meters)")
        hitEffText = ROOT.TLatex(.62, .91, "#scale[0.6]{Overall Efficiency: " + str(self.OverallEff(nLayer)) + "}")
        hitEffText.SetNDC(ROOT.kTRUE)
        hitEffText.Draw()

        c2.SaveAs("{0}/{1}.pdf".format(self.outDir, "LayerHitEff"+plotID))
        return

    def TwoDiskHitEff(self):
        # Setup canvas
        c3 = ROOT.TCanvas("c3", "c3", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)

        # Layer hits
        diskHitPosPlot = ROOT.TH2D("diskhits", "Layer 0 OR 1 AND 2 OR 3 Hit Efficiency", 520,-1.30,1.30,520,-1.3,1.3)
        self.tChain.Draw("y:x>>diskhits",
                         "(layerHits[0]==1 || layerHits[1]==1) && (layerHits[2]==1 || layerHits[3]==1)", "colz")
        # Fill edges of disk so that they show up in plot
        for xBin in range(1, diskHitPosPlot.GetNbinsX()+1):
            for yBin in range(1, diskHitPosPlot.GetNbinsY()+1):
                val = diskHitPosPlot.GetBinContent(xBin,yBin)
                x = abs(diskHitPosPlot.GetXaxis().GetBinCenter(xBin))
                y = abs(diskHitPosPlot.GetYaxis().GetBinCenter(yBin))
                if val == 0 and x < self.endcapOuterRad and y < self.endcapOuterRad:
                    yMax = (self.endcapOuterRad**(2)-x**(2))**(0.5)
                    xMax = (self.endcapOuterRad**(2)-y**(2))**(0.5)
                    if x <= self.endcapInnerRad:
                        yMin = (self.endcapInnerRad**(2)-x**(2))**(0.5)
                    else:
                        yMin = -yMax
                    if y <= self.endcapInnerRad:
                        xMin = (self.endcapInnerRad**(2)-y**(2))**(0.5)
                    else:
                        xMin = -xMax
                    if xMin < x and x < xMax and yMin < y and y < yMax:
                        diskHitPosPlot.SetBinContent(xBin, yBin,0.01)
        # Layer hits
        allPosPlot = ROOT.TH2D("allpos", "Layer 0 OR 1 AND 2 OR 3 Hit Efficiency", 520,-1.30,1.30,520,-1.3,1.3)
        self.tChain.Draw("y:x>>allpos", "", "colz")
        # Divide hit positions by all positions
        diskHitPosPlot.Divide(allPosPlot)
        diskHitPosPlot.Draw("colz")
        # Plot settings
        diskHitPosPlot.GetYaxis().SetTitle("y (meters)")
        diskHitPosPlot.GetXaxis().SetTitle("x (meters)")
        hitEffText = ROOT.TLatex(.62, .91, "#scale[0.6]{Overall Efficiency: " + str(self.TwoDiskOverallEff()) + "}")
        hitEffText.SetNDC(ROOT.kTRUE)
        hitEffText.Draw()

        c3.SaveAs("{0}/TwoDiskHitEff.pdf".format(self.outDir))
        return

    def LayerEtaEff(self, nLayer, highEta=False):
        if nLayer >= 3:
            print("Please enter a layer below layer 3.")
            return
        # Setup canvas
        c4 = ROOT.TCanvas("c4", "c4", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)
        nLayer1 = str(nLayer)
        nLayer2 = str(nLayer+1)
        plotID = nLayer1+nLayer2

        # Layer hits eta
        highEtaArg = ""
        highEtaTag = ""
        lowerEtaBound = 1.2
        upperEtaBound = 3.0
        if highEta:
            highEtaArg = " && eta > 1.4 && eta < 2.9"
            highEtaTag = "HighEta"
            lowerEtaBound = 1.57
            upperEtaBound = 2.85
        hitEtaPlot = ROOT.TH1D("hiteta"+plotID, "Layer {0} OR {1} Eta Efficiency".format(nLayer1, nLayer2), 180,lowerEtaBound,upperEtaBound)
        self.tChain.Draw("eta>>hiteta"+plotID,
                         "(layerHits["+nLayer1+"]==1 || layerHits["+nLayer2+"]==1) && pt > 0.5"+highEtaArg, "")

        # All eta
        allEtaPlot = ROOT.TH1D("alleta"+plotID, "Layer {0} OR {1} Eta Efficiency".format(nLayer1, nLayer2), 180,lowerEtaBound,upperEtaBound)
        self.tChain.Draw("eta>>alleta"+plotID, "pt > 0.5"+highEtaArg, "")
        # Base plot for formatting
        baseEtaPlot = hitEtaPlot.Clone("baseeta"+plotID)
        baseEtaPlot.Reset()
        if highEta:
            baseEtaPlot.GetYaxis().SetRangeUser(0.90, 1.00)
        else:
            baseEtaPlot.GetYaxis().SetRangeUser(0, 1.5)
        baseEtaPlot.Draw()
        # Divide hit eta by all etta
        etaEffPlot = ROOT.TEfficiency(hitEtaPlot, allEtaPlot)
        etaEffPlot.Draw("same")
        # Plot settings
        baseEtaPlot.GetXaxis().SetTitle("#eta")

        c4.SaveAs("{0}/{1}.pdf".format(self.outDir, "LayerEtaEff"+plotID+highEtaTag))
        return

    def LayerEtaPtEff(self, nLayer):
        if nLayer >= 3:
            print("Please enter a layer below layer 3.")
            return
        # Setup canvas
        c5 = ROOT.TCanvas("c5", "c5", 400, 400) 
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetNumberContours(255)
        nLayer1 = str(nLayer)
        nLayer2 = str(nLayer+1)
        plotID = nLayer1+nLayer2

        # Layer hits eta/pt
        hitEtaPtPlot = ROOT.TH2D("hitetapt"+plotID, "Layer {0} OR {1} Eta/pt Efficiency".format(nLayer1, nLayer2), 200,0,10,180,1.2,3.0)
        self.tChain.Draw("eta:pt>>hitetapt"+plotID,
                         "layerHits["+nLayer1+"]==1 || layerHits["+nLayer2+"]==1", "")
        # All eta/pt
        allEtaPtPlot = ROOT.TH2D("alletapt"+plotID, "Layer {0} OR {1} Eta/pt Efficiency".format(nLayer1, nLayer2), 200,0,10,180,1.2,3.0)
        self.tChain.Draw("eta:pt>>alletapt"+plotID,
                         "", "")

        # Divide hit positions by all positions
        hitEtaPtPlot.Divide(allEtaPtPlot)
        hitEtaPtPlot.Draw("colz")
        # Plot settings
        hitEtaPtPlot.GetYaxis().SetTitle("#eta")
        hitEtaPtPlot.GetXaxis().SetTitle("p_{T}")

        c5.SaveAs("{0}/{1}.pdf".format(self.outDir, "LayerEtaPtEff"+plotID))
        return

def Plot(inPath, outDir, verbose=False):
    if not os.path.isdir(outDir): os.mkdir(outDir)
    # Start plotting
    plots = ChronoPlots(inPath, outDir)
    if verbose:
        print("Using data in {}".format(inPath))
        print("Saving plots to {}".format(outDir))
    # Plot layer hits
    for i in range(0, 4):
        # if verbose: print("Plotting layer {}".format(i))
        # plots.TwoDiskHitEff()
        # if verbose: print("Plotted hit two-disk hit efficiency.")
        # plots.LayerHits(i)
        # if verbose: print("Plotted hits.")
        if i < 3:
            # plots.LayerHitEff(i)
            # if verbose: print("Plotted hit efficiency.")
            # plots.TwoLayerHits(i)
            # if verbose: print("Plotted two-layer hits.")
            plots.LayerEtaEff(i)
            if verbose: print("Plotted eta efficiency.")
            plots.LayerEtaEff(i, highEta=True)
            if verbose: print("Plotted high eta efficiency.")
            # plots.LayerEtaPtEff(i)
            # if verbose: print("Plotted eta/pt efficiency.")

    if verbose: print("Finished.")
    return


if __name__ == "__main__":
    import sys
    # Ensure no graphs are drawn to screen and no root messages are sent to terminal
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    # Set in and out directories
    inPath = sys.argv[1]
    outDir = "out/"+(inPath.split("out_v2-0-0_")[-1]).split(".")[0]
    # Check for verbosity
    isVerbose = (len(sys.argv) > 1 and sys.argv[-1] == "-v")
    Plot(inPath, outDir, verbose=isVerbose)
