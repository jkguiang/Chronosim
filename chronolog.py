import json
import os

class Output:
    def __init__(self, outFile="./out.json", sf=0.001, verbose=False):
        self.outFile = outFile
        self.output = {}
        self.didStart = False
        self.curLayer = 0
        self.curQuad = 0
        self.sf = sf
        self.verbose = verbose

    def IsValidFile(self, inFile):
        """ Check for valid file """
        isLogFile = (inFile.split(".")[-1] == "txt" and "log" in inFile)
        return (os.path.isfile(inFile) and isLogFile)
    
    def Write(self):
        with open(self.outFile, "w") as fout:
            json.dump(self.output, fout, indent=4)
            if self.verbose: print("Wrote output to {}".format(self.outFile))

        return

    def HandleLGAD(self, lgad):
        """ Handle output for a strip of LGADs """
        if not self.didStart: return
        curXPos = 0
        for out in lgad:
            param = out.split(" = ")
            if param[0] == "x":
                curXPos = float(param[1])*self.sf
                if curXPos not in self.output[self.curLayer][self.curQuad]:
                    self.output[self.curLayer][self.curQuad][curXPos] = []
            elif param[0] == "y":
                self.output[self.curLayer][self.curQuad][curXPos].append(float(param[1])*self.sf)

        return

    def HandleQuad(self, quad):
        """ Handle output from start of a new quadrant """
        if not self.didStart: return
        for out in quad:
            param = out.split(" = ")
            if param[0] == "nQuad":
                self.curQuad = int(param[1])
                if self.curQuad not in self.output[self.curLayer]:
                    self.output[self.curLayer][self.curQuad] = {}

        return

    def HandleStart(self, start):
        """ Handle output from start of a new layer """
        for out in start:
            param = out.split(" = ")
            if param[0] == "layer":
                self.curLayer = int(param[1])
                if self.curLayer not in self.output:
                    self.output[self.curLayer] = {}
            if param[0] == "z" and param[0] not in self.output[self.curLayer]:
                self.output[self.curLayer]["z"] = float(param[1])*self.sf
        
        self.didStart = True
        return

    def ParseFile(self, inFile):
        """ Parse valid log file """
        if not self.IsValidFile(inFile):
            print("ERROR: Invalid file type / File does not exist")
            return
        if self.verbose: print("Parsing file {}".format(inFile))
        with open(inFile, "r") as fin:
            allLines = fin.readlines()
            for line in allLines:
                splitLine = (line.split("\n")[0]).split(", ")
                if "START" in splitLine[0]:
                    self.HandleStart(splitLine[1:])
                elif "QUAD" in splitLine[0]:
                    self.HandleQuad(splitLine[1:])
                else:
                    self.HandleLGAD(splitLine[1:])
        return

if __name__ == "__main__":
    out = Output(verbose=True)
    out.ParseFile("txt/dMod-3x2_315mmInnerRad_log0.txt")
    out.Write()


