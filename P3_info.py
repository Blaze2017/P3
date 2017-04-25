# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 02:40:22 2017

@author: Frank
"""

#Import the San Jose xml file into Ptyhon as a class
import xml.etree.cElementTree as ET
import pprint
import codecs
import json
import collections
import csv

#Overview the imported data -- Find out how many tags there are in the map data
data = '//Mac/Home/Desktop/projects/project 3/san-jose_california.osm'
tags = {}
elements = ET.iterparse(data)
for event, elem in elements:
    if elem.tag in tags: 
        tags[elem.tag] += 1
    else:
        tags[elem.tag] = 1
pprint.pprint(tags)

#Find out how many users contributing to this map data
elements = ET.iterparse(data)
def users(fname):
    user = set()
    for _, element in elements:
        for ele in element:
            if 'uid' in ele.attrib:
                user.add(ele.attrib['uid'])
    return user
users_con = users(data)
print(len(users_con))

import signal
import subprocess
import os
import pymongo

#pro = subprocess.Popen('mongod', preexec_fn = os.setsid)
from pymongo import MongoClient
dbName = 'testmap'

# Get connected to MongoDB
client = MongoClient('localhost:27017')
db = client[dbName]

# Define several paths used in future commands
IN = data[:data.find('.')]
json_file = data + '.json'
SJ = db[IN]             

#check file sizes
import os
print 'The original OSM file is {} MB'.format(os.path.getsize(data)/1.0e6) # convert the unit bytes to megabytes
print 'The JSON file is {} MB'.format(os.path.getsize(data + ".json")/1.0e6) # convert the unit bytes to megabytes 

#Check number of documents                   
SJ.find().count()

#check number of unique users
len(SJ.distinct('created.user'))

#Check number of Nodes and Ways
print "The total counts of nodes:",SJ.find({'type':'node'}).count()
print "The total  counts of ways:",SJ.find({'type':'way'}).count()

#Find out the top 5 cuisine in San Jose
cuisines = SJ.aggregate([{"$match":{"amenity":{"$exists":1},
                                 "amenity":"restaurant",}},      
                      {"$group":{"_id":{"Food":"$cuisine"},
                                 "count":{"$sum":1}}},
                      {"$project":{"_id":0,
                                  "Food":"$_id.Food",
                                  "Count":"$count"}},
                      {"$sort":{"Count":-1}}, 
                      {"$limit":6}])
print(list(cuisines))
 
#Find out the top 5 post codes in San Jose
Pcode = SJ.aggregate( [ 
    { "$match" : { "address.postcode" : { "$exists" : 1} } }, 
    { "$group" : { "_id" : "$address.postcode", "count" : { "$sum" : 1} } },  
    { "$sort" : { "count" : -1}},
      {"$limit":5}] )
print(list(Postcode))                        