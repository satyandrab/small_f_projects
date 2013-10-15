'''
Created on Aug 14, 2013

@author: satyandra.babu
'''

import urllib2
import re
from lxml import html

import csv
output = open("writersstore_sample1.0.csv", "wb")
csv_writer = csv.writer(output)
csv_writer.writerow(['link', 'title', 'sub_title', 'level', 'published_dt', 'events', 'keywords', 'authors', 'toc', 'images', 'description', 'type'])


def main():
    count = 1
    url = 'http://www.writersstore.com/courses'
    html_response1 = urllib2.urlopen(url)
    
    html_source = html_response1.read()
    result = html_source.replace('\n', '').replace('\r', '')
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    for i in range(1, 7):
        page_urls = 'http://www.writersstore.com/courses?page='+str(i)
        
        html_response1 = urllib2.urlopen(page_urls)#.read().replace('\n', '').replace('\r', '')
    
        html_source = html_response1.read()
        result = html_source.replace('\n', '').replace('\r', '')
        parsed_source = html.fromstring(result, url)
        parsed_source.make_links_absolute()
        
        url_data = parsed_source.xpath("//td[@class='products_text']/a/@href")
        for urls_d in url_data:
            print urls_d
            count = count+1
            print count
            print '*'*78

def get_details(url):
    html_response1 = urllib2.urlopen(url)
    
    html_source = html_response1.read()
    result = html_source.replace('\n', '').replace('\r', '')
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    link = url
    title =  "".join(parsed_source.xpath("//h1/text()"))
    print link
    print title
#        thumbnail = ["".join(div_d.xpath("a/img/@src")).replace('?image_crop_resized=180x145','')]
#        Description = "".join(div_d.xpath("div[@class = 'grey gradient-fade']/text()")).strip()
#        csv_writer.writerow([link, title, '', '', '', '', '', '', '', thumbnail, Description, ''])

        

if __name__ == "__main__":
    get_details('http://www.writersstore.com/developing-a-tv-pilot-ellen-sandler/')