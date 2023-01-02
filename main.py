#!/bin/python3 
import os, sys, subprocess
import json, time
import traceback
# from pymongo import MongoClient
import googleapiclient.discovery as gAPI
import shutil


from Resources.ytSetup import yt_Program_Setup
from Resources.removeTags import TagRemover
# Debug Var     
_Debug_Active = False 
_Output_Loc = 2
if len(sys.argv) > 1:
    if sys.argv[1] == "--debug":
        _Debug_Active = True 
        _Output_Loc = 3

# Log Var     
TIME_FORMAT ='%H:%M:%S'
        
class yt_App: 
    
    
    def __init__(self):
        # Setup DB links and API 
        self._ProgramSetup = yt_Program_Setup()
        # Program Constants
        # Status Codes 
        self._StatusCodes = ['Completed', 'Failed', 'Downloading']
        # General Setup 
        self._API_KEY, self._DB, self._COLLECTION, self._YT_Client = None, None, None, None 
        self._LOG = None 
        self._Settings = None 
        
        # Program User
        self._User = None 
        
        # Video Prefix Constant
        self._YT_Begin = "https://youtu.be/" # All youtube videos, when shared, have this url shortcut attached to the tag
        
        self._PlaylistURL = None 
        self._SaveVideoDirectory = None 
        self._TempVidDirectory = None 

        # Database Records
        self._Vids, self._Cntr, self._oldVids, self._compareVids = list(), 0, dict(), list()
        
        # Variables to Hold Upload DAta
        # { date: { videoURL : [] } }
        self._VidDict = list() 
        self._CurrDate = time.strftime('%Y-%d-%m')
        
        # Tag removing program
        self._TagRemoveProgram = None 
        
        self.ErrorCnt = 0 
        
        

    def setupProgram(self): 
        # Setup Program
        self._ProgramSetup.setup()
        # Assign Necessary Connection Values
        self._API_KEY, self._YT_Client, self._LOG = self._ProgramSetup.getKey(), self._ProgramSetup.getYTRef(), self._ProgramSetup.getLogRef()
        self._COLLECTION = self._ProgramSetup.getDBRef()
        self._Settings = (self._ProgramSetup.getSettings())
        try: 
            if self._Settings is not None: 
                self._PlaylistURL = self._Settings['playlistID']
                self._SaveVideoDirectory = self._Settings['saveDirectory']
                self._User = self._Settings['user']
        except Exception as err: 
            self._LOG.output(3, f"{time.strftime(TIME_FORMAT)} ---> There was an error retrieving data from settings file : \n{err}\n")
            exit(-1)
        
    
      
    # This will create a list of video tags in the playlist
    def queryYT(self): 
        if self._PlaylistURL is None: 
            self._LOG.output(3, f"{time.strftime(TIME_FORMAT)} ---> Error: No Playlist URL Specified")
            exit(-1)
        
        next_Page_Token, yt_Response = None, None
        # Output A Status Update to Log File
        self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Attempting YT Query...")
        
        while True: 
            try:  
                # Get the Response 
                yt_Response = self._YT_Client.playlistItems().list(
                    part = 'contentDetails',
                    playlistId = self._PlaylistURL, 
                    pageToken = next_Page_Token  
                ).execute()
                  
                # Loop Through the Items in the Query
                for tags in yt_Response['items']: 
                    self._Vids.append(tags['contentDetails']['videoId'])
                    self._Cntr += 1      
                    
            except Exception as err: 
                self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> \'queryYT\' had an Error: {err}\n")
                exit(-1)
            
                
            # Check if there is another page, otherwise break out
            try: 
                next_Page_Token = yt_Response['nextPageToken']
            except Exception as err:
                break
        
        # Report Query Was Successful
        self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> YT Query Executed Successfully!")
    
        
        if _Debug_Active:
            # Debug Print
            for i, items in enumerate(self._Vids): 
                print(f"{i}:\t{items}")
            
            print(len(self._Vids))
    
    # Create Fields
    def saveToDict(self, videoID, status=None): 
        self._VidDict.append({"user" : self._User, "name": '', "artist" : '', "videoTag" : videoID, "status" : status})
        
       

    def uploadData(self):
        # Before Uploading, lets check if the item already exists, and if so, check the Status 
        # We want to update the status if it is different, without actually creating a new documents
        # this would save space
        for items in self._VidDict: 
            try:
                if self.checkPrev(items['videoTag']) == 0:
                    self._COLLECTION.addData(items['user'], items['name'], items['artist'], items['videoTag'],items['status'])     
                else: 
                    self._COLLECTION.updateFailedStatus(items['user'], items['videoTag'], items['status'])
            except Exception as err: 
                self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> There was an error uploading to the database ---> Error: \n{err}\n")
                self.ErrorCnt += 1 
                
        self._COLLECTION.commitAdditions()
                

    
    
    def checkForPastVids(self): 
        self._oldVids = self._COLLECTION.getQueryObj().where('user', '==', self._User)
        if not self._oldVids: return 
        tempArr = list()
        # Now Grab All The Video Ids and save it temporarily, then replace old_Vids dict with this new array
        for data in self._oldVids.stream(): 
            tempHold = data.to_dict()
            tempArr.append({'videoTag' : tempHold['videoTag'], 'status' : tempHold['status']})
        self._oldVids = tempArr
        if _Debug_Active: 
                self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Old Video IDS:\n{self._oldVids}")
     
            
    def checkPrev(self, videoId) -> int: 
        '''Returns 0 if the item does not already exist
           Returns 1 if the items does exist
        '''
        if len(list(self._oldVids)) == 0: 
            return 0 
        for data in self._oldVids: 
            # If the video matches and it was previously downloaded succesfully, then return 1, indicating there is no need
            # Or we may need to
            # download it again if we find the videoTag and it was not previously downloaded successfully try again
            if videoId == data['videoTag'] and data['status'] == self._StatusCodes[0]: 
                return 1 
            elif videoId == data['videoTag'] and data['status'] == self._StatusCodes[1]:
                return 1
       
        return 0 
            
            
    
    
    def download(self): 
            
        self._TempVidDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Videos")
        if not os.path.exists(self._TempVidDirectory): 
            os.mkdir(self._TempVidDirectory)
            
        # Now Change the Directory since I cant modify the output of yt-dlp 
        os.chdir(self._TempVidDirectory)
            
        # Now Loop and download vids
        for i, videoTag in enumerate(self._Vids): 
            statusCode = self._StatusCodes[2]
            try: 
                if self.checkPrev(videoTag) == 0 and not ('--fillDatabase' in sys.argv): 
                    subprocess.run(['yt-dlp', '-fm4a', "--embed-thumbnail", "--embed-metadata", (str(self._YT_Begin) + str(videoTag))], check=True)
            except Exception as err: 
                self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Video {i} : {videoTag} ---> error: \n{err}\n")
                statusCode = self._StatusCodes[1]
                self.ErrorCnt += 1 
            # Check if the video failed to download or not
            if statusCode != "Failed": 
                statusCode = self._StatusCodes[0]
            # Save the video to the dictionary
            self.saveToDict(videoTag, statusCode)
            if _Debug_Active: 
                self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> DEBUG ACTIVE, 1 VIDEO LIMIT ACTIVE")
                return 
      
      
    def cleanMusicTags(self): 
        if('--fillDatabase' in sys.argv): return
        self._TagRemoveProgram = TagRemover(self._TempVidDirectory, '[')
        self._TagRemoveProgram.run()
        self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> All Tags Cleaned!")
    
    
    def moveMusic(self): 
        if('--fillDatabase' in sys.argv): return
        if not os.path.exists(self._SaveVideoDirectory): 
            self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Error: {self._SaveVideoDirectory} Not Found")
            self.ErrorCnt += 1
            return 
        
        for root, _, files in os.walk(self._TempVidDirectory): 
            for aFile in files: 
                try: 
                    shutil.move(os.path.join(root,aFile), self._SaveVideoDirectory)
                except Exception as err: 
                    self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Error: {err}")

        self._LOG.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> All Downloaded Videos Have Been Moved!")
        
            
            
    def runTime(self): 
        
        # Main Program Run 
        self.setupProgram()
        self.checkForPastVids()
        self.queryYT()
        self.download()
        self.uploadData()
        # Do The Clean Up 
        self.cleanMusicTags()
        self.moveMusic()
        
        # Output End Message
        if self.ErrorCnt > 0: 
            # Output the Program Was Successfully Ran but with errors
            self._LOG.output(_Output_Loc,f"{time.strftime(TIME_FORMAT)} ---> Program Executed With Errors!\nError Count: {self.ErrorCnt}")
        else: 
            # Output the Program Was Successfully Ran 
            self._LOG.output(_Output_Loc,f"{time.strftime(TIME_FORMAT)} ---> Program Execution Successful!")
       
        # End the Program 
        self._ProgramSetup.closeProgram()
        
        
        
     
if __name__ == "__main__": 
    main=yt_App()
    main.runTime()
        
