import os, sys, subprocess
from pathlib import Path

closingTags : dict[str,str] = {
    '(' : ')', 
    '[' : ']'
    
    
}

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
            
    
    def cleanName(self, fileName: str, bSeperator: chr) -> tuple[bool,str] : 
        nameOfFile, extension = os.path.splitext(fileName)
        retStr = ''
        openCharacter, closeCharacter = bSeperator, ''
        indexOpen, indexClose = 0,0
        
        try:
            closeCharacter = closingTags[bSeperator]
        except Exception as e:
            print(f"Error, could not get closing character from character's dict, please verify your opening character has a closed character defined")
            print(f"\nDefaulting to old Algorithm")
            return self.cleanNameBackup(fileName, bSeperator)
        try:
            indexOpen = nameOfFile.rindex(openCharacter)
        except Exception as e: 
            return False, fileName
        
        try:
            indexClose = nameOfFile.rindex(closeCharacter)
        except Exception as e : 
            print(f'Alert: Could not find closing character "{closeCharacter}, for file {fileName} defaulting to old algorithm"')
            return self.cleanNameBackup(fileName, bSeperator)
        
        # Check if the indexclose is at the begginging or end of the string, since this would impact what gets modified
        if(nameOfFile[indexClose+1:] == None):
             retStr = nameOfFile[0:indexOpen] + nameOfFile[indexClose:] 
        else:
            retStr = nameOfFile[0:indexOpen] + nameOfFile[indexClose+1:]
        # Handle An Extra Space at the End of the Cleaned File Name
        if(retStr[len(retStr) - 1] == ' '):
            retStr = retStr[0:len(retStr)-1]
        # Connect the filename with the extension
        retStr = retStr + extension
        finalStr = retStr
        # Recurse here until all the words within the tags are removed
        if(nameOfFile.find(bSeperator) != -1) : 
            finalStr = self.cleanName(retStr, bSeperator)[1]
        if(finalStr == os.path.splitext(fileName)[0]):
            return False, finalStr
        
        return True, finalStr
    
    def cleanNameBackup(self, fileName: str, bSeperator: chr) -> "tuple[bool, str]" : 
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
                    print("here")
                    print(destName)
                    # os.rename(srcName, os.path.join(root, destName))
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
       
