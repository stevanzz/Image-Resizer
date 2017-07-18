# Copyright 2015, PocketLabs Sdn Bhd, Shoppr Labs Sdn Bhd 
# Author : Marcus Low m@shopprapp.com

from django.db import models
from djangotoolbox.fields import ListField, DictField, SetField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager

class GenericModels (models.Model):
    def __init__(self, *args, **kwargs):
        super(GenericModels, self).__init__(*args, **kwargs)
        self.data = list()
        self.result = "success"
    #__init__
    
    data = ListField()
    result = models.CharField(max_length=255)
    

class UserContent (models.Model) :
    
    ImageLocation   = models.CharField(max_length=512)             # url in amazons3 also serves as the tag
    Tags            = DictField()                                                   # Tags for Color, Brand, Category
    Email           = models.CharField(max_length=255)             # our key to the other database
    CreatedOn       = models.DateTimeField(auto_now_add=True)                       # date time 
    Particulars     = DictField()
    
    class MongoMeta:
        indexes = [
            [('ImageLocation',1)],
            [('Email',1)],
            [('CreatedOn', -1)]
        ]    
    
    objects = MongoDBManager()
    

class Comments (models.Model) :
    
    Email           = models.CharField(max_length=255)
    Comment         = models.CharField(max_length=255)
    ImageID         = models.CharField(max_length=512) 
    CreatedOn       = models.DateTimeField(auto_now_add=True)   # date time
    Particulars     = DictField() # deleted : bool, by_admin : emailid (if deleted)    
    
    class MongoMeta:
        indexes = [
            [('Email',1)],
            [('ImageID',1)],
            [('CreatedOn', -1)]
        ]
     
    
""" the story of Likes and Follow 

If a user unlike, we store the unlike date to this same object
if the user like the same thing, we dont revert, we create a new object and store the like
basically we will never delete the like and unlike
Same for Follow and unfollow
Why this is important because it allows us to get data of the retailers fans, assuming these content
are OOTDs by the ambassadors of the retailers. We know when ppl like them, Follow them and when they stopped doing so 
and when they came back.

"""
    
class Likes (models.Model) :
    
    ImageID         = models.CharField(max_length=512)           # unique hash for this image calc from url
    Email           = models.CharField(max_length=255)
    CreatedOn       = models.DateTimeField(auto_now_add=True)   # date time
    Unliked         = models.BooleanField(default=False)        # if unliked
    UnlikedDate       = models.DateTimeField(null = True, auto_now_add=False)   # date time  
    
    class MongoMeta:
        indexes = [
            [('Email',1)],
            [('ImageID',1)],
            [('CreatedOn', -1)]
        ]
    
    
class Follow (models.Model) :
    
    EmailIdol       = models.CharField(max_length=255)         # our key to the other database
    EmailFollower   = models.CharField(max_length=255)
    CreatedOn       = models.DateTimeField(auto_now_add=True)   # date time
    Unfollowed      = models.BooleanField(default=False)        # if unliked
    UnfollowedDate  = models.DateTimeField(null = True, auto_now_add=False)  # date time
    
    class MongoMeta:
        indexes = [
            [('EmailIdol',1)],
            [('EmailFollower',1)],
            [('CreatedOn', -1)]
        ]
    
    
class Flagged (models.Model) :
    ImageID         = models.CharField(max_length=512, db_index = True)           # unique hash for this image calc from url
    Email           = models.CharField(max_length=255)
    Reason          = models.CharField(max_length=255)
    CreatedOn       = models.DateTimeField(auto_now_add=True)   # date time    
    
       
# DELETABLE OBJECTS
# These are used to track callbacks, eg apns 
# 
import datetime

class Notification (models.Model) :
    Email      = models.CharField(max_length=255)
    Device     = models.CharField(max_length=255)
    Content    = DictField()
    CreatedOn  = models.DateTimeField(auto_now_add=True,default = datetime.datetime.now())   # date time
    
    class MongoMeta:
        indexes = [
            [('Email',1),('CreatedOn',-1)]
            ]
          
 
# Devices to Arns 
 
class DeviceToARN (models.Model) :
    Device  = models.CharField(max_length=255, db_index = True)    
    Arn     = models.CharField(max_length=255, db_index = True)    
    
    
class Promotion (models.Model) :
    CategoryText = models.CharField(max_length=255)
    CreatedOn =  models.DateTimeField(auto_now_add=True,default = datetime.datetime.now())
    
        
    
    
