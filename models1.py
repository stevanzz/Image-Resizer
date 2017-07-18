# Copyright 2014, PocketLabs Sdn Bhd, Shoppr Labs Sdn Bhd 
# Author : Marcus Low m@shopprapp.com

from django.db import models
from djangotoolbox.fields import ListField, DictField, SetField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager

#==============================================================================
# Products classes.
# OnlineRetailerName: Zalora, Asos, Dressabelle, Lovebonito, mango 
# Brands: mango, adidas, something borrowed
#==============================================================================

''' This class contains information about online retailer '''

class OnlineRetailer(models.Model):
    # Holds name of online retailer.   
    Name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.Name
    
#============================================================================== 

class OnlineRetailerRegion (models.Model) :
    
    """ This model is unique. Its not derived directly during scrapping/mapping but its a by product
      of reseeding 
      """    
    
    # Holds name of online retailer.   
    Name = models.CharField(max_length=255)
    Country = models.CharField(max_length=16)
    
    class Meta :
        unique_together = [("Name", "Country")]
    
    def __str__(self):
        return "{}/{}".format(self.Country, self.Name)
    
#============================================================================== 

class BrandRegion (models.Model) :
    
    """ This model is unique. Its not derived directly during scrapping/mapping but its a by product
    of reseeding 
    """
    
    # Holds name of online retailer.   
    Brand = models.CharField(max_length=255)
    Country = models.CharField(max_length=16)
    
    class Meta :
        unique_together = [("Brand", "Country")]
    
    def __str__(self):
        return "{}/{}".format(self.Country, self.Brand)    

#============================================================================== 

''' This class contains information about product '''
class ProductDescriptionRegion (models.Model):  
    
    CountryRetailer = models.CharField(max_length=255)
    
    Country = models.CharField(max_length=8)
    
    # combo of Country, retailer, productid
    
    UniqueKey = models.CharField(max_length=255, unique = True)
    
    # Holds name of online retailer. 
    OnlineRetailerName = models.CharField(max_length=255)
    
    # Holds product id (123123)
    ProductId = models.CharField(max_length=255)
    
    # Brand
    Brand = models.CharField(max_length=255)
    
    # can be rounded up
    PriceValue = models.IntegerField(default = 0)
    
    #type
    Type = models.CharField(max_length=100)
    
    # Holds update date.
    UpdateDateTime = models.DateTimeField()

    # Holds json data.
    Content = DictField()
   
    # Holds creation date.
    CreatedOn  = models.DateTimeField(auto_now_add=True)
      
    class Meta :
        unique_together = [("CountryRetailer", "ProductId")]    
    
    class MongoMeta:    
        
        indexes =   [
            [('CountryRetailer',1)],
            [('ProductId',1)],
            [('Country',1)],
            [('OnlineRetailerName',1)],
            [('UniqueKey', 1)],
            [('Type',1)],
            [('Type',1), ('PriceValue',1)],
            [('CreatedOn', -1)],
            [('UpdateDateTime',-1)]
        ]    
        
    objects = MongoDBManager()
    
    def __str__(self):
        return (self.Country + "/" + self.OnlineRetailerName + '/' + self.ProductId)

#==============================================================================
    
class BrandsAnalyticsSingleton (models.Model) :
    Brands = DictField()
    objects = MongoDBManager()
    
    def __str__(self):
        return ('Brands Object, total: ' + str(len(self.Brands.keys())))   
    
class SpecialLists (models.Model) :
    Lists = DictField()
    objects = MongoDBManager()

    def __str__(self):
        return ('Lists object, total: ' + str(len(self.Lists.keys())))   
#==============================================================================
# Users classes.
#==============================================================================

''' These types are not the limit, just some predefined ones, feel free to add '''
TypesOfLink = { 
    "fb" : "facebook",
    "twitter" : "twitter",
    "pinterest" : "Pinterest",
    "google" : "Google+"
    }

''' Holds information about user
NOTE: In current implementation one user may have one device and User.Name = deviceId 
In Particulars :
    All specific platform must conform to the keyword token.
    Example : Facebook
    fb_name 
    fb_email
    fb_id
    fb_age
    
    
brands preferences are stored in : Particulars['Brands']
'''
Particulars_Preference_Brands = "Brands"
Particulars_Preference_Styles = "styles"
Particulars_Preference_Occasion = "occasion"
Particulars_Preference_Color = "colours"

class User(models.Model):
    # the linking to the user should be any data that uniquely identifies the user
    # it can be email, with each successive id linking the user replacing  
    # a more obscure one
    Name        = models.CharField(max_length=255)
    CreatedOn   = models.DateTimeField(auto_now_add=True)
    Particulars = DictField()
    Email       = models.CharField(max_length=255)
    Password    = models.CharField(max_length=255) 
    
    NextOnlineRetailerIndex = models.IntegerField(default = 0)
    UserContentOldestViewDate = models.DateTimeField(null=True)

    class MongoMeta:
        indexes =   [
            [('Email', 1)],
            [('CreatedOn', -1)]
        ]    
        
    
    objects = MongoDBManager()
    
    def __str__(self):
        return self.Email + ' ' + str(self.CreatedOn)

''' Holds datetime of swipe made or api request for this user '''
class AccessTimeline(models.Model):
    Email = models.CharField(max_length=255)
    #DeviceId = models.CharField(max_length=255)
    Date = models.DateTimeField()
    
    def __str__(self):
        return self.Email + ' ' + str(self.Date)
    
class ViewedProductDescription(models.Model):
    Email = models.CharField(max_length=255, db_index = True)
    OnlineRetailerName = models.CharField(max_length=255)
    ProductId = models.CharField(max_length=255)
    
    def __str__(self):
        return self.Email + ' ' + self.OnlineRetailerName + ' ' + self.ProductId
    
    
class Point(models.Model):
    #in order
    latitude = models.FloatField(default=0)
    longtitude = models.FloatField(default=0)
    
    def __str__ (self) :
        return "{},{}".format(self.latitude, self.longtitude)
    

class WishListRegion(models.Model) :
    
    Email = models.CharField(max_length=255)
    OnlineRetailerName = models.CharField(max_length=255)
    ProductId   = models.CharField(max_length = 255)
    PriceLike   = models.DecimalField(max_digits=6, decimal_places=2)
    Currency    = models.CharField(max_length = 255)
    UniqueKey   = models.CharField(max_length = 255)
    Country     = models.CharField(max_length=8)   
    Geo         = Point()
    CreatedOn   = models.DateTimeField(auto_now_add=True)
    
    
    class Meta :
        unique_together = [("Email", "UniqueKey")]  
        
    class MongoMeta:
        indexes =   [
            [('UniqueKey',1)],
            [('OnlineRetailerName',1)],
            [('Country',1)],
            [('Email', 1)],
            [('CreatedOn', -1)],
            [('CreatedOn',-1),('Email',1)]            
        ]    
        
    objects = MongoDBManager()
    
    def __str__(self):
        return u"{}:{}".format(self.Email,self.UniqueKey)  


class Board(models.Model): 
        # will make a a board object for each tag,
        # this means that we can follow the changes in each of the tags  
        # each tag/untag is then tracked, 
        # may help to understand how users are using the boards?
        # may need to support multiple tag submit but will leave that for later...
        Email       = models.CharField(max_length=255)
        Tag        = models.CharField(max_length=255) 
        Content     = DictField()      
        BoardType        = models.CharField(max_length=30) # should be product or ootd
        ImageLocation   = models.CharField(max_length=512)  # s3  image location for product or ootd
        Privacy   = models.CharField(default = "public",max_length=100) # the privacy group of an item, this could be, "public", 'private' or maybe a group at some point
        Deleted     = models.BooleanField(default=False)
        CreatedOn   = models.DateTimeField(auto_now_add=True)
        DeletedOn   = models.DateTimeField(null=True)
        # additional indexing on the Email AND Image in the how this would make queries faster
        class MongoMeta:
            indexes = [
                [('Email', 1)],
                [('CreatedOn', -1)],
                [('Tag',1),('Email',1)]
                ]
        
        objects = MongoDBManager()    
        def __str__(self):
            return self.Email + ' ' + str(self.CreatedOn) + ' ' + self.Tag

class Point(models.Model):
    #in order
    latitude = models.FloatField(default=0)
    longtitude = models.FloatField(default=0)
    
    def __str__ (self) :
        return "{},{}".format(self.latitude, self.longtitude)


class LikeAnalytic(models.Model):
    Email = models.CharField(max_length=255)
    OnlineRetailerName  = models.CharField(max_length=255) #OnlineRetailer.Name, zalora, asos, mds...
    ProductId = models.CharField(max_length=255) #Pure ID, sku 
    DateSwipe = models.DateTimeField()
    AmbianceLight = models.CharField(null = True, max_length=255) #lux value, channel 0, channel 1
    Geolocation = EmbeddedModelField(Point)
    Like = models.BooleanField()
    
    class MongoMeta:
        indexes =   [
            [('Email', 1)],
            [('OnlineRetailerName',1)],
            [('ProductId',1)],
            [('DateSwipe', -1)]
        ]     
    
    def __str__(self):
        return self.Email + ' ' + self.OnlineRetailerName + ' ' + self.ProductId

class BuyClickAnalytic(models.Model):
    Email = models.CharField(max_length=255)
    OnlineRetailerName  = models.CharField(max_length=255)
    ProductId = models.CharField(max_length=255)
    DateSwipe = models.DateTimeField()
    AmbianceLight = models.CharField(null = True, max_length=255) #lux value, channel 0, channel 1
    Geolocation = EmbeddedModelField(Point)
    
    class MongoMeta:
        indexes =   [
            [('Email', 1)],
            [('DateSwipe', -1)]
        ]        
    
    def __str__(self):
        return self.Email + ' ' + self.OnlineRetailerName + ' ' + self.ProductId
    
class ProductEmailed(models.Model):
    Email               = models.CharField(max_length=255)
    OnlineRetailerName  = models.CharField(max_length=255)
    ProductId           = models.CharField(max_length=255)
    CreatedOn           = models.DateTimeField(auto_now_add=True)
    Extras              = DictField()      
    class MongoMeta:
        indexes =   [
            [('CreatedOn', 1)],
        ]        
        
    def __str__(self):
        return self.Email + ' ' + self.OnlineRetailerName + ' ' + self.ProductId

#==============================================================================

class Ticket (models.Model) :
    Code        = models.CharField(max_length=128) 
    Email       = models.CharField(max_length=255) 
    DateStart   = models.DateTimeField()    
    DateEnd     = models.DateTimeField()
    
    class MongoMeta:
        indexes =   [
            [('Email', 1)],
            [('Code', 1)]
        ]            
    
#==============================================================================

"""
items.find({
    created_at: {
        $gte: ISODate("2010-04-29T00:00:00.000Z"),
        $lt: ISODate("2010-05-01T00:00:00.000Z")
    }
})
"""

class TicketRedemption (models.Model) :
    Code        = models.CharField(max_length=128) 
    Email       = models.CharField(max_length=255) 
    DateUsed    = models.DateTimeField()   

    class MongoMeta:
        indexes =   [
            [('Email', 1)],
            [('Code', 1)]
        ]            

#==============================================================================


# if this user exist, then ....yeah he is active, else...we add counter to his swipes
# we only store this if its mod % 5 

class TicketActiveUser (models.Model) :
    
    Email         = models.CharField(max_length=255)
    ActivityCount = models.IntegerField(default=0)
    
    class MongoMeta:
        indexes =   [
            [('Email', 1)]
        ]           

