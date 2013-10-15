'''
Created on Aug 14, 2013

@author: satyandra.babu
'''

import urllib2
import re
from lxml import html

import csv
output = open("mozcome_sample1.0.csv", "wb")
csv_writer = csv.writer(output)
csv_writer.writerow(['link', 'title', 'sub_title', 'level', 'published_dt', 'events', 'keywords', 'authors', 'toc', 'images', 'description', 'type'])


def main():
    url = 'http://moz.com/academy'
    html_response1 = urllib2.urlopen(url)#.read().replace('\n', '').replace('\r', '')
    
    html_source = html_response1.read()
    result = html_source.replace('\n', '').replace('\r', '')
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    div_data = parsed_source.xpath("//div[@class='span2 thumbnail thumbnail-paid']")
    for div_d in div_data:
        link = "".join(div_d.xpath("a/@href"))+'?refid=skilledup'
        title =  "".join(div_d.xpath("h5/text()"))
        thumbnail = ["".join(div_d.xpath("a/img/@src")).replace('?image_crop_resized=180x145','')]
        Description = "".join(div_d.xpath("div[@class = 'grey gradient-fade']/text()")).strip()
        csv_writer.writerow([link, title, '', '', '', '', '', '', '', thumbnail, Description, ''])
        print '*'*78
        

if __name__ == "__main__":
    main()