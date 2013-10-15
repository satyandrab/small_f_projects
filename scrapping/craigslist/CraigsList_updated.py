import urllib2
import urllib
import mechanize
import cookielib
import BeautifulSoup
import csv
import re
#from urllib import urlretrieve
#import urlparse
import os
import sys
import time
#import MySQLdb
from UnicodeWriter import UnicodeWriter
from htmlentitydefs import name2codepoint 
pattern = re.compile(r'&(?:(#)(\d+)|([^;]+));')

br = mechanize.Browser()
# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),
                      max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux \
i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
# The site we will navigate into, handling it's session
today = time.strftime('%Y_%m_%d')
file=open('craigsList_albanyga'+today+'.csv','wb')
UnicodeWriterObj = UnicodeWriter(file)
UnicodeWriterObj.writerow(['URL','Name','Location', 'Email', 'Description','Date','Phone'])

def main():
    #ExtractDetails('http://raleigh.craigslist.org/apa/3275803941.html')
    
    
    CreatedURL = 'http://albanyga.craigslist.org/apa/'
    ExtractLandingURL(str(CreatedURL))
    for i in range(100, 500, 100):
        SummaryURL = 'http://albanyga.craigslist.org/apa/index'+str(i)+'.html'
        print "*"*45
        print SummaryURL
        print "*"*45
        ExtractLandingURL(str(SummaryURL))
        
def ExtractLandingURL(URL):
    #try:
    print URL
    responseHtml = br.open(URL)
    soup = BeautifulSoup.BeautifulSoup(responseHtml)
    URLRe = re.compile('/apa/\d+[10].html')
    URLList = URLRe.findall(str(soup))
    print URLList
    for url in URLList:
        url = 'http://albanyga.craigslist.org'+str(url)
        ExtractDetails(str(url))
    #except:
    #    pass
    
def ExtractDetails(URL):
    try:
        dataList = []
        dataList.append(str(URL))
        responseHtml = br.open(URL)
        soup = BeautifulSoup.BeautifulSoup(responseHtml)

        ######################### Title #############################
        try:
            RawTitle = soup.find("h2");
            Title = ExtractTags(str(RawTitle))
            Title = str(Title).strip()
            #Title = str(Title).replace(',', ';')
            Title = handle_html_entities(str(Title))
            dataList.append(Title) 
        except:
            Title = ''
            dataList.append(Title) 
        ######################## Location ##########################    
        try:
            LocationRe = re.compile('.*?\((.*?)\).*')
            Location = LocationRe.findall(str(Title))
            #Location = str(Location).strip()
            #Location = str(Location).replace(',', ';')
            Location = ExtratData(str(Location))
            Location = handle_html_entities(str(Location))
            dataList.append(Location)
        except:
            Location = ''
            dataList.append(Location)
        ####################### Email ########################
        try:
            mailsoup = str(soup).replace('\n', '')
            EmailRe = re.compile("var displayEmail = .(.*?).;")
            Email = EmailRe.findall(str(mailsoup))
            #print Email
            dataList.append(Email[0])
        except:
            Email = ''
            dataList.append(Email)
        ####################### vFlyer ########################
        """
        try:
            VFLYERsoup = str(soup).replace('\n', '')
            VFLYERRe = re.compile('VFLYER ID: (\d+)<')
            VFlyerID = VFLYERRe.findall(str(VFLYERsoup))
            vflyerid = VFlyerID[0]
            dataList.append(vflyerid)
        except:
            vflyerid = ''
            dataList.append(vflyerid)
        """
        
        ####################### Description ########################
        try:
            descsoup = str(soup).replace('\n', '')
            DescriptionRe = re.compile('<div id="userbody">(.*?)<!-- START CLTAGS -->')
            RawDescription = DescriptionRe.findall(str(descsoup))
            Description = ExtractTags(str(RawDescription))
            Description = str(Description).strip()
            Description = str(Description).replace('\\t', '')
            Description = str(Description).replace('\\r', '')
            Description = ExtratData(str(Description))
            Description = handle_html_entities(str(Description))
            Description = str(Description).replace('\xc2\xa0', '')
            dataList.append(Description)
        except:
            Description = ''
            dataList.append(Description)
        
        ################# Images ##########################
        """
        try:
            out_folder="\\images\\"
            imgsoup = str(soup).replace('\n', '')
            ImageRe = re.compile('<img src="(.*?\.jpg)"')
            RawImageURL = ImageRe.findall(str(imgsoup))
            for imgURL in RawImageURL:
                nameRaw = str(imgURL).split('/')
                filename = str(nameRaw[-1])
                curpath = os.path.abspath(os.curdir)\
                outpath = os.path.join(out_folder, filename)
                outpath = curpath+outpath
                a, b=urlretrieve(imgURL, outpath)
                ImagePath = '\\images\\'+filename      
                dataList.append(str(ImagePath))                
        except:
            ImagePath = ''
            dataList.append(ImagePath)
            dataList.append(',')
        """
        
        ####################### Date ########################
        try:
            Datesoup = str(soup).replace('\n', '')
            DateRe = re.compile('Date:(.*?),')
            Date = DateRe.findall(str(Datesoup))
            #print Date
            dataList.append(Date[0])   
        except:
            Date = ''
            dataList.append(Date)
            
#        ####################### Address ########################
#        try:
#            addresssoup = str(soup).replace('\n', '')
#            addressRe = re.compile('<!-- CLTAG region=.*?-->(.*?)<small>')
#            address = addressRe.findall(str(addresssoup))
#            print address
#            dataList.append("".join(address).strip())   
#        except:
#            Date = ''
#            dataList.append(Date)

        
        ####################### Phone ########################
        try:
            Phonesoup = str(soup).replace('\n', '')
            PhoneRe = re.compile('(\d{3}-\d{3}-\d{4})|(\(\d{3}\)\s*\d{3}-\d{4})|(\s+\d{3}-\d{4})')
            Phone = PhoneRe.findall(str(Phonesoup))
            for phone in Phone:
                if phone[0]:
                    dataList.append(phone[0])   
                if phone[1]:
                    dataList.append(phone[1])
                if phone[2]:
                    dataList.append(phone[2])
        except:
            PhoneNo = ''
            dataList.append(PhoneNo)
            
        print "+"*45
        print dataList
        print "+"*45
            
        UnicodeWriterObj.writerow(dataList)
    except:
        pass

def ExtractTags(HTML):
    p1 = re.compile(r'<.*?>|<|>|&quot;');
    text = p1.sub('', HTML);
    return text;

def ExtratData(data):
    data = data.replace('[','')
    data = data.replace(']','')
    data = data.replace("'",'')
    data = data.strip()
    return data

def replace(match):
    if match.group(1):
        return unichr(int(match.group(2)))
    elif match.group(3) in name2codepoint.keys():
        return unichr(name2codepoint[match.group(3)])
    else:
        return ""
 
def handle_html_entities(string):
    return pattern.sub(replace, unicode(string, 'utf-8'))


if __name__ == "__main__":
    main()

