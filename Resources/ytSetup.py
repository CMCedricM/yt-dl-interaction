#!/bin/python3 
import os, sys, json, time, requests
# from pymongo import MongoClient
import googleapiclient.discovery as gAPI

# Logging 
from Resources.Logging import LOGGING 
from Resources.database.fire import fireBase


# Debug Var     
_Debug_Active = False 
_Output_Loc = 2
if len(sys.argv) > 1:
    if sys.argv[1] == "--debug":
        _Debug_Active = True 
        _Output_Loc = 3

# Log Var     
TIME_FORMAT ='%H:%M:%S'
        
 
 
# This class will:
# 1. Establish a link to the database holding history of prev saved youtube videos 
# 2. Establish a link to youtube using the key 
class yt_Program_Setup: 
    
    def __init__(self): 
        # Program Constants 
        self.JSONFILE = os.path.join(os.path.dirname(__file__), os.path.join("secrets", "secrets.json"))
        # self._DBNAME, self._COLLNAME = "YT-DL", "video-history"
        self._DBNAME, self._COLLNAME = "yt-analyzer", "video-history"
        # Logging and Settings 
        self._LogFile, self._LogsFolder = None, None   
        self._JsonSettings, self._JsonSettingsPath= None, None 
        
        
        self._API_KEY = None 
        self._Collection, self._Vid_HistoryDataBase = None, None 
        self._YT_Conn = None 
        
        # Startup Functions 
        self.setupProgramLog()
  
    def setupProgramLog(self): 
        
        self._JsonSettingsPath = os.path.join(os.path.join(os.path.dirname(__file__), "settings"), "settings.json")
        # Firs attempt to create the log files from the json settings file if it exists
        if os.path.exists(self._JsonSettingsPath):
            try: 
                self._JsonSettings = json.load(open(self._JsonSettingsPath)) 
                self._LogFile = LOGGING(self._JsonSettings['logOutputFolder'])
            except Exception as err: 
                pass 
            else: 
                return 
        
        # If the json settings file does not exist or the file couldn't be created, just create a log in the program directory
        self.__setupLog()
            
  
    def __setupLog(self): 
        # Set the Log Folder Path, likely migrate to MongoDB Later
        self._LogsFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
        # Now Check if the Logs Folder Exists if, not then crate it 
        if not os.path.exists(self._LogsFolder):
            os.mkdir(self._LogsFolder)
        # Create the log file 
        self._LogFile = LOGGING(os.path.join(self._LogsFolder, f'{time.strftime("%Y%d%m-%H%M")}.txt'))
    
           
    # Load Necessary Connection URL's / API Keys      
    def loadConnections(self): 
        # Lets First Check We Have Internet 
        try: 
            res = requests.get('https://www.youtube.com')
        except Exception as err: 
            self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Error Establishing Internet Connection!!! --->\n{err}\n")
            self._LogFile.closeFile()
            exit(-1)
        else: 
            if (res.status_code != 200):
                self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Error Establishing Website Connection!!! --->\n{res.status_code} : {res.reason}\n")
                self._LogFile.closeFile()
                exit(-1)
            else: 
                self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Connection to Youtube Established...")
        # Lets Load the Json File First
        self.JSONFILE = json.load(open(self.JSONFILE))
        # Lets Load Appropriate Keys/URLS
        self._API_KEY = self.JSONFILE["Keys"]["YT-Key"]
        self._Collection = self.JSONFILE["URLS"]["MongoDB"]
        
    def linkDatabase(self): 
         # Output Attempt to Connect To DB
        self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Attempting Connection to User Database")
        self._Collection = fireBase()
        self._Collection.setupConnections()
        
        if _Debug_Active:
            print(f"Function \'linkDataBase\' Types ---> {type(self._Collection)}")
            
    
    # # Create Link to DataBase 
    # def linkDatabase_old(self): 
    #     # Output Attempt to Connect To DB
    #     self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Attempting Connection to User Database")
    #     # Attempt to Establish a Link to the Database 
    #     client = MongoClient(self._DataBase)
    #     # Check if the Link was Successful
    #     try: 
    #         client.server_info()
    #     except Exception as err: 
    #         self._LogFile.output(_Output_Loc, f"{time.strftime('%H:%M')} ---> Error Establishing Link!!! --->\n{err}\n")
    #         exit(-1)
    #     # Now set DataBase Var to the Actual Database, not the url  
    #     self._DataBase = client[self._DBNAME]
    #     # Now Set The Collection to the Correct Collection
    #     self._Collection = self._DataBase[self._COLLNAME]
        
    #     if _Debug_Active:
    #         print(f"Function \'linkDataBase\' Types ---> {type(self._DataBase), type(self._Collection)}")


    # Actually Establish my link to YT
    def linkToYT(self): 
        try: 
            self._YT_Conn = gAPI.build("youtube", "v3", developerKey=self._API_KEY)
        except Exception as err: 
            self._LogFile.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Error Establishing YT Link --->\n{err}\n")
            exit(-1)
        
       
       
        
    # Getter Functions, since ion want to inherit later on, for organization purposes  
    #
    def getDBRef(self): #-> tuple[pymongo.database.Database, pymongo.collection.Collection]: 
        return self._Collection
    
    def getYTRef(self): 
        return self._YT_Conn
    
    def getKey(self) -> str:
        return self._API_KEY
    
    def getLogRef(self) -> LOGGING: 
        return self._LogFile
    
    def getSettings(self): 
        return self._JsonSettings
    
    def closeProgram(self): 
        self._LogFile.closeFile()
    #
    # End Getter Functions 

    def setup(self): 
        # Lets First Load The Connection Vars 
        self.loadConnections()
        # Now Lets Link to the Database
        self.linkDatabase()
        # Lets Link to youtube
        self.linkToYT()
        # Since The Key Was Loaded and a DB link was successful 
        self._LogFile.output(_Output_Loc, f"{time.strftime(TIME_FORMAT)} ---> Connection to Database \'{self._DBNAME}\' and collection \'{self._COLLNAME}\' was successful!")
        
     
