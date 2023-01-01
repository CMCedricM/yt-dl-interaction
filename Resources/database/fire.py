import firebase_admin, os
from firebase_admin import credentials,firestore
from uuid import uuid4


class fireBase: 

    def __init__(self) -> None:
       pass
        
    
    def setupConnections(self) -> None : 
        self.cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'serviceKey.json'))
        self.app = firebase_admin.initialize_app(self.cred)
        self.firestore_client = firestore.client()
        self.coll_ref = self.firestore_client.collection("videos")
        
    def debugFirebase(self) -> dict: 
        print("Performing Test Query...")
        query_ref = self.coll_ref.where('user', '==', 'cedric-men')
        for items in query_ref.stream(): 
            return (f"{items.id} => {items.to_dict()}")
    
    def addData(self, name, user, status, artist, videoTag) -> None: 
  
        # Create a new uuid, aka a document title
        video_ref = self.coll_ref.document(str(uuid4()).replace('-', '')[:20])
        # Now actually create the doc
        video_ref.set({
            'name' : name,
            'user' : user, 
            'status' : status, 
            'artist' : artist,
            'videoTag' : videoTag, 
        })
    
    # I may want to create a limit on how many times the program should attempt re-download
    # In this function the idea is to first grab the reference of the document that holds the user's failed video download
    # this requires the 'user' and the 'videoTag' to match in the query, so that ion update the wrong items
    def updateFailedStatus(self, user, videoTag) -> None: 
        '''This program attempts to re-download a failed video every time the program is re-run, if the item succeeds the status is 
        updated to 'completed' otherwise it stays as 'failed' '''
        pass
        
    
        
    
    
        

        




if __name__ == '__main__':
   app = fireBase()
   app.setupConnections()
   app.debugFirebase()
   app.addData('test', 'test', 'test', 'test', 'test')