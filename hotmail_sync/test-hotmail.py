#http://sourceforge.net/projects/pywbxml.berlios/files/latest/download
#https://github.com/diegows/pywbxml/blob/master/0.1/INSTALL
import requests
import base64
import sys
import zlib
from lxml import etree
#from pywbxml import *
from pprint import pprint
from StringIO import StringIO

s = requests.Session()
s.auth = ('projecttesting1000@hotmail.com', 'nublado123')

#url = "https://m.hotmail.com/Microsoft-Server-ActiveSync"
url = "https://bay-m.hotmail.com/Microsoft-Server-ActiveSync"

opts_headers = {
    'Host' : 'm.hotmail.com' }

print '---options---'
r = s.options(url, headers=opts_headers)
pprint(r.headers)
print '-------'

params = {
    'Cmd' : 'FolderSync',
    'User' : 'projecttesting1000@hotmail.com',
    'DeviceId' : 'v140',
    'DeviceType' : 'SmartPhone' }


headers = {
    'Host' : 'm.hotmail.com',
    'MS-ASProtocolVersion' : '14.0',
    'Content-Type' : 'application/vnd.ms-sync.wbxml',
    'User-Agent' : 'Apple-iPhone/705.18',
    'Accept-Encoding' : 'gzip' }


fsync = u"""<?xml version="1.0"?><!DOCTYPE AirSync PUBLIC "-//AIRSYNC//DTD AirSync//EN" "http://www.microsoft.com/"><FolderSync xmlns="http://synce.org/formats/airsync_wm5/folderhierarchy"><SyncKey>0</SyncKey></FolderSync>
"""

data = fsync
#datawb = xml2wbxml(data)
r = s.post(url, params=params, headers=headers, data=data)

print 'REQ', data
print 'RESP', r.status_code
print 'URL', r.url
print dir(r)
pprint(r.request.headers)
pprint(r.headers)
#print r.content.read()
resp = r.content#wbxml2xml(r.content)
print 'RESP BODY', resp

#Search
params = {
    'Cmd' : 'Search',
    'User' : 'projecttesting1000@hotmail.com',
    'DeviceId' : 'v140',
    'DeviceType' : 'SmartPhone' }


headers = {
    'Host' : 'm.hotmail.com',
    'MS-ASProtocolVersion' : '14.0',
    'Content-Type' : 'application/vnd.ms-sync.wbxml',
    'User-Agent' : 'Apple-iPhone/705.18',
    'Accept-Encoding' : 'gzip' }

search = u"""<?xml version="1.0"?><!DOCTYPE AirSync PUBLIC "-//AIRSYNC//DTD AirSync//EN" "http://www.microsoft.com/">
<Search xmlns="Search" xmlns:airsync="AirSync">
<Store>
  <Name>Mailbox</Name>
    <Query>
      <And>
        <airsync:CollectionId>7</airsync:CollectionId>
        <FreeText>Presentation</FreeText>
      </And>
    </Query>
    <Options>
      <RebuildResults />
      <Range>0-4</Range>
      <DeepTraversal/>
    </Options>
  </Store>
</Search>
"""

#data = xml2wbxml(search)
r = s.post(url, params=params, headers=headers, data=search)

print 'REQ', search
print 'RESP', r.status_code
print 'URL', r.url
pprint(r.request.headers)
pprint(r.headers)
resp = r.content#wbxml2xml(r.content)
print 'RESP BODY', resp

