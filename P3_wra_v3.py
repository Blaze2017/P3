# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 20:24:57 2017

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
filein = '//Mac/Home/Desktop/projects/project 3/sample.osm'
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


#Solve the stree name inconsitency problem
import re
from collections import defaultdict

str_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

standard_strname = ["Avenue", "Boulevard", "Commons", "Court", "Drive", "Lane", "Parkway", 
                         "Place", "Road", "Square", "Street", "Trail"]

pair = {'Ave'  : 'Avenue',
           'Blvd' : 'Boulevard',
           'Dr'   : 'Drive',
           'Ln'   : 'Lane',
           'Pkwy' : 'Parkway',
           'Rd'   : 'Road',
           'Rd.'   : 'Road',
           'St'   : 'Street',
           'street' :"Street",
           'Ct'   : "Court",
           'Cir'  : "Circle",
           'Cr'   : "Court",
           'ave'  : 'Avenue',
           'Hwg'  : 'Highway',
           'Hwy'  : 'Highway',
           'Sq'   : "Square"}


def audit_street(datafile):
    datafile = open(datafile, "r")
    strtype = defaultdict(set)
    for line, elem in ET.iterparse(datafile, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    strsearch = str_type_re.search(tag.attrib['v'])
                    if strsearch:
                        street_type = strsearch.group()
                        if street_type not in standard_strname:
                            strtype[street_type].add(street_type)    
    return strtype

strtype = audit_street(data)

pprint.pprint(dict(strtype))



#Update the street names
def update_name(name, pair, regex):
    regsearch = regex.search(name)
    if regsearch:
        street_type = regsearch.group()
        if street_type in pair:
            name = re.sub(regex, pair[street_type], name)

    return name

for street_type, ways in strtype.iteritems():
    for name in ways:
        standarized_name = update_name(name, pair, str_type_re)
        print name, "=>", standarized_name



#zip code checking

from collections import defaultdict

#define the creteria to judge if the zip code is not good
def zCode(NVZCode, zipcode):
    doubleDigi = zipcode[0:2]
    
    if not doubleDigi.isdigit():
        NVZCode[doubleDigi].add(zipcode)
    
    elif doubleDigi != 95:
        NVZCode[doubleDigi].add(zipcode)
        

#check the zip code one by one
def audit_zipcodes(osmfile):
    osm_file = open(osmfile, "r")
    NVZCode = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:postcode":
                    zCode(NVZCode,tag.attrib['v'])

    return NVZCode
#collect the invaid zip codes and print them out
SJzCodes = audit_zipcodes(data)
pprint.pprint(dict(SJzCodes))

#Update zip codes
#Define a function about how to change the invaid zip codes to valuesid zip codes
def updateZP(zipcode):
    IsNum = re.findall('[a-zA-Z]*', zipcode)
    if IsNum:
        IsNum = IsNum[0]
    IsNum.strip()
    if IsNum == "CA":
        ZCprocess = (re.findall(r'\d+', zipcode))
        if ZCprocess:
            if ZCprocess.__len__() == 2:
                return (re.findall(r'\d+', zipcode))[0] + "-" +(re.findall(r'\d+', zipcode))[1]
            else:
                return (re.findall(r'\d+', zipcode))[0]
#Update the invaid codes one by one
for street_type, ways in SJzCodes.iteritems():
    for name in ways:
        appro_ZP = updateZP(name)
        print name, "=>", appro_ZP
        
        
        
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    """Parses element from iterparse, cleans address, and returns dictionary"""
    node = {}
    if element.tag == "way":
    	  node['node_refs'] = []
    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        attrs = element.attrib 
        node['created'] = {}
        for attr in attrs: 
            if attr == "lat" or attr == "lon":
                if 'pos' not in node:
                    node['pos'] = []
                if attr == 'lat':
                    node['pos'].insert(0,float(element.attrib[attr]))
                elif attr == 'lon':
                    node['pos'].insert(1,float(element.attrib[attr]))
            elif attr in CREATED:
        	    node['created'][attr] = element.attrib[attr]
            else:
                node[attr] = element.attrib[attr]    
        for subtag in element.iter('tag'):
            key, value = subtag.attrib['k'], subtag.attrib['v']
            if problemchars.match(key):
                continue
            elif lower_colon.match(key):
                subtagjsonkey = key.split(':')
                if subtagjsonkey[0] == 'addr':
                    if 'address' not in node:
                    	  node['address'] = {}
                    if subtagjsonkey[1] == 'street':
                        node['address'][subtagjsonkey[1]] = update_name(value, pair,str_type_re)
                    elif subtagjsonkey[1] == 'postcode':
                        node['address'][subtagjsonkey[1]] = updateZP(value)
                elif subtagjsonkey[0] == 'turn':
                    continue
                else:
                    node[subtagjsonkey[1]] = value             
            else:
                if ':' not in key:
                    if key == "exit_to":
                        node[key] = update_name(value, pair, str_type_re )
                    else:
                        node[key] = value
        if element.tag == "way":                    
            for subtag in element.iter('nd'):
                node['node_refs'].append(subtag.attrib['ref'])      
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    """writes dictionary to json file and returns data"""
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

process_map(filein, True)