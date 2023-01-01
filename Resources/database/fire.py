import firebase_admin, os, sys
from firebase_admin import credentials,firestore
from uuid import uuid4


class fireBase: 

    def __init__(self) -> None:
        self._CollectionName = 'video-history'
        
    
    def setupConnections(self) -> None : 
        self.cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'serviceKey.json'))
        self.app = firebase_admin.initialize_app(self.cred)
        self.firestore_client = firestore.client()
        self.coll_ref = self.firestore_client.collection(self._CollectionName)
        
    def debugFirebase(self) -> dict: 
        print("Performing Test Query...")
        query_ref = self.coll_ref.where('user', '==', 'cedric-men')
        for items in query_ref.stream(): 
            return (f"{items.id} => {items.to_dict()}")
    
    def addData(self, user, name, artist, videoTag, status) -> None: 
  
        # Create a new uuid, aka a document title
        video_ref = self.coll_ref.document(str(uuid4()).replace('-', '')[:20])
        # Now actually create the doc
        video_ref.set({
            'user' : user,
            'name' : name, 
            'artist' : artist,
            'videoTag' : videoTag, 
            'status' : status, 
        })
    
    # I may want to create a limit on how many times the program should attempt re-download
    # In this function the idea is to first grab the reference of the document that holds the user's failed video download
    # this requires the 'user' and the 'videoTag' to match in the query, so that ion update the wrong items
    def updateFailedStatus(self, user, videoTag, status) -> None: 
        '''This program attempts to re-download a failed video every time the program is re-run, if the item succeeds the status is 
        updated to 'completed' otherwise it stays as 'failed' '''
        doc_ref = self.coll_ref.where('user', '==', user).where('videoTag', '==', videoTag)
        # We have to iterate through because we are likely being given a pointer that needs to converted to a different type
        for items in doc_ref.stream():
            doc_ref = items.id
        if doc_ref:
            doc_ref = self.coll_ref.document(doc_ref)
            doc_ref = doc_ref.update({'status' : status})
    
    
        
    
        
    
    
        

        




if __name__ == '__main__':
   app = fireBase()
   app.setupConnections()
   print(app.debugFirebase())
   if '--debugAdd' in sys.argv:
        app.addData('test', 'test', 'test', 'test', 'test')
   app.updateFailedStatus('cedric-men', 'hy3R_4kyRn0', 'failed')