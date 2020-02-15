from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from datetime import datetime
import os
import numpy as np
from pathlib import *

from ..base import constants as c

##############
# PhotoCrypt #
##############

class PhotoCrypt():
    def __init__(self,db,working_directory,hash_init_opt):
        ### Variables Definition
        self.db=db # Database
        self.public_key=serialization.load_der_public_key(open(c.public_key_file,"rb").read(),default_backend())
        self.private_key=None
        self.working_directory=Path(working_directory)
        self.hash_init_opt=hash_init_opt
        self.images_dict=dict()
        self.security_warnings_list=[]

    #######################
    # Pure RSA Management #
    #######################

    def padding(self):
        return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)

    def checkIfLoaded(self):
        return self.private_key!=None

    def loadRsaKey(self):
        if not self.db.checkDecrypted():
            raise AssertionError("Database not decrypted")

        self.private_key=serialization.load_der_private_key(bytes(self.db.getOption("RSA_PRIV"),'8859'),None,default_backend())

        if self.public_key.public_numbers()!=self.private_key.public_key().public_numbers():
            self.warning("Public key did not match the public key, possible tampering with the public key file.")
            self.public_key=self.private_key.public_key()
            open(c.public_key_file,"wb").write(self.public_key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo))

    def encryptRSA(self,b):
        try:
            return self.public_key.encrypt(b,self.padding())
        except:
            return None

    def decryptRSA(self,b):
        if not self.checkIfLoaded():
            raise AssertonError("Private Key not loaded")
        try:
            return self.private_key.decrypt(b,self.padding())
        except:
            return None

    def newRsaKey(self):
        if not self.db.checkDecrypted():
            raise AssertionError("Database not decrypted")

        self.private_key=rsa.generate_private_key(public_exponent=65537,key_size=2048*4,backend=default_backend())
        self.public_key=self.private_key.public_key()

        open(c.public_key_file,"wb").write(self.public_key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo))
        self.db.setOption("RSA_PRIV",self.private_key.private_bytes(serialization.Encoding.DER,serialization.PrivateFormat.TraditionalOpenSSL,serialization.NoEncryption()))

    #######################
    # Pure AES Management #
    #######################

    def encryptAES(self,b,key):### Check if fernet really works
        try:
            return Fernet(key).encrypt(b)
        except:
            return None

    def decryptAES(self,b,key):
        try:
            return Fernet(key).decrypt(b)
        except:
            return None

    def genAES(self):
        return Fernet.generate_key()

    ########################
    # Low Level Managmenet #
    ########################

    def dateToBytes(self,dt):
        return dt.second+60*(dt.minute+60*(dt.hour+24*(dt.day-1+31*(dt.month-1+12*(dt.year-1)))))

    def bytesToDate(self,n):
        second=n
        minute=second//60
        hour=minute//60
        day=hour//24
        month=day//31
        year=month//12

        second=second%60
        minute=minute%60
        hour=hour%24
        day=day%31+1
        month=month%12+1
        year=year+1

        return datetime(year,month,day,hour,minute,second)

    def now(self):
        return self.dateToBytes(datetime.now())

    def imageToBytes(self,image): # returns image,date
        return bytes(list(image.flatten()))+b"\x00"*16

    def bytesToImage(self,b): # Image, If Ok (not scrambled)
        l=list(b)
        return np.array(l[:-16]).reshape(*c.camera_image_dims).astype(np.uint8),l[-16:]==[0]*16

    ##################
    # Hash Functions #
    ##################

    def hashImage(self,image):
        digest=hashes.Hash(hashes.SHA256(),backend=default_backend())
        digest.update(self.imageToBytes(image))
        return digest.finalize()

    def hashImages(self):
        if not self.db.checkDecrypted():
            raise AssertionError("Database not decrypted")
        sum=int(self.db.getOption(self.hash_init_opt))
        for image in self.images_dict.values():
            sum+=int.from_bytes(self.hashImage(image),'big')
            sum%=(1<<32*8)
        return sum.to_bytes(32,'big')

    def newHashInit(self):
        self.db.setOption(self.hash_init_opt,int.from_bytes(os.urandom(32),'big'))

    def checkHash(self):
        hash=open(self.working_directory.joinpath(c.hash_file_name),"rb").read()
        if hash!=self.hashImages():
            self.warning("Images hash does not match. Possible tampering with images or deletion of an image.")

    def reHash(self):
        open(self.working_directory.joinpath(c.hash_file_name),"wb").write(self.hashImages())


    #########################
    # High Level Management #
    #########################

        #####################################################################################################
        # Image file structure: RSA(Image_flattened[1280*720*3] + \x00*16[16])+aes_key[44] {date_bytes.aes} #
        #####################################################################################################

    def warning(self,warning):
        self.security_warnings_list.append(warning)

    def dumpWarnings(self):
        l=self.security_warnings_list
        self.security_warnings_list=[]
        return l

    def loadImage(self,file):
        if not self.checkIfLoaded():
            raise AssertonError("Private Key not loaded")
        if file[-4:]!='.aes':
            return

        ### Reading encrypted image and date
        b=open(self.working_directory.joinpath(file),"rb").read()
        filename=file[:-4]
        ok=False

        ### Decrypting aes key and image
        aes_key=self.decryptRSA(b[-c.fernet_key_length:])
        if aes_key!=None:
            image_crypt=self.decryptAES(b[:-c.fernet_key_length],aes_key)
            if image_crypt!=None and len(image_crypt)==c.camera_image_dims[0]*c.camera_image_dims[1]*c.camera_image_dims[2]+16:
                image,ok=self.bytesToImage(image_crypt)

        ### Checking if image was decrypted properly
        if not ok:
            self.warning("Image with name {name}.aes cannot be decoded. Possible tampering with the image file.".format(filename))
            self.deleteImageFile(file)
        else:
            self.images_dict[filename]=image

    def loadImages(self):
        if not self.checkIfLoaded():
            raise AssertonError("Private Key not loaded")

        for file in os.listdir(self.working_directory):
            self.loadImage(file)
        self.checkHash()

    def saveImage(self,image,filename):
        ### Adding to dictionary
        self.images_dict[filename]=image

        ### Encrypting Image and AES Key
        aes_key=self.genAES()
        b=self.imageToBytes(image)
        crypted_image=self.encryptAES(b,aes_key)
        crypted_aes=self.encryptRSA(aes_key)
        hash=open(c.hash_file_name,"rb").read()
        if crypted_aes==None:
            crypted_aes=""
            hash=0

        ### Opening files
        image_file=open(self.working_directory.joinpath(filename+".aes"),"wb")
        hash_file=open(self.working_directory.joinpath(c.hash_file_name),"wb")

        ### Writing to files
        image_file.write(crypted_image+crypted_aes)
        hash_file.write(((int.from_bytes(hash,'big')+int.from_bytes(self.hashImage(image),'big'))%(1<<32*8)).to_bytes(32,'big'))

    def deleteImageFile(self,file):
        os.remove(self.working_directory.joinpath(file))

    def deleteImage(self,file):
        if not self.checkIfLoaded():
            raise AssertonError("Private Key not loaded")

        self.deleteImageFile()
        self.images_dict.pop(file)
        self.reHash()

    def deleteAllImages(self):
        for file in os.listdir(self.working_directory):
            if file!=c.hash_file_name:
                os.remove(self.working_directory.joinpath(file))

        self.images_dict=dict()
        self.reHash()

    def checkImage(self,file):
        return file in self.images_dict

    def getImage(self,file):
        return self.images_dict[file]

    def listImages(self):
        return list(zip(self.images_dict.values(),self.images_dict.keys()))
