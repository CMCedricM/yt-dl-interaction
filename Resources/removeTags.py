import os, sys, subprocess
from pathlib import Path

class TagRemover: 
    
    def __init__(self, dirName:str, bSeperator: chr): 
        self._DirName = Path(dirName)
        self._beginSeper = bSeperator
        self._modCount = 0 
      
        
    def checkForPath(self): 
        if not os.path.exists(self._DirName): 
            print(f"\nError, the path {self._DirName} can not be located!", end="\n\n")
            print("If the Path has any spaces, please enclose the name of the directory with quotation marks!")
            print("Ex: /home/Hello World/example -> /home/\"Hello World\"/example\n")
            exit(-1)
            
    
    
    def cleanName(self, fileName: str, bSeperator: chr) -> "tuple[bool, str]" : 
        nameOfFile, extension = os.path.splitext(fileName)
        tempStr, appendToWord, wasMod = '', True, False
        
        
        for words in nameOfFile.split(): 
            for chars in words: 
                if chars == bSeperator: 
                    appendToWord = False 
                    wasMod = True
            if appendToWord: 
                tempStr += (words + " ")   
            appendToWord = True 
        
        # Re-appened the extension, but remove the last space in the tempStr, return mod string if mod
        if wasMod: 
            return wasMod, (tempStr[:len(tempStr)-1] + extension)
        else: # Return original string 
            return wasMod, fileName
        

    def renameFiles(self):
        for root, dirs, files in os.walk(self._DirName): 
            for aFilename in files: 
                srcName = os.path.join(root, aFilename)
                wasModified, destName = self.cleanName(aFilename, self._beginSeper)
                if wasModified:
                    os.rename(srcName, os.path.join(root, destName))
                    print(f"File Renamed: {aFilename} -> {destName} ")
                    self._modCount += 1 
                


    def run(self): 
        print(f"\nDirectory Entered: {self._DirName}")
        self.checkForPath()
        self.renameFiles()
        print(f"Number of Modified File Names: {self._modCount}")




if __name__ == "__main__": 
    
    if len(sys.argv) < 5: 
        print(f"Error Usage: python {os.path.basename(__file__)} -d <dir> -c <charSeperator>")
        exit(-1)
    
    main = TagRemover(sys.argv[2], sys.argv[4])
    main.run()
       
