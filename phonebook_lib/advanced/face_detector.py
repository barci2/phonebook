import face_recognition as faces
import numpy as np
import json

from ..base import constants as c

class FaceDetector():
    def __init__(self,db,warning_signal):
        self.db=db
        self.warning=warning_signal
        self.embedding=None

    def loadEmbedding(self):
        if not self.db.checkDecrypted():
            raise AssertionError("Database not decrypted")
        self.embedding=np.array(json.loads(self.db.getOption("FACE_EMBEDDING")))

    def setFace(self,image):
        embedding=faces.face_encodings(image,num_jitters=100)
        if len(embedding)>1:
            self.warning("More than one face detected")
            return
        self.embedding=embedding[0]
        self.db.setOption("FACE_EMBEDDING",json.dumps(list(self.embedding)))

    def checkFace(self,image):
        if type(self.embedding)==type(None):
            raise AssertionError("Embedding not loaded")
        embedding=faces.face_encodings(image)
        return all(faces.compare_faces(embedding,self.embedding)) and len(embedding)>0
