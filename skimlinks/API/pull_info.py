import urllib2
from xml.dom.minidom import parseString
import re
import csv
from UnicodeWriter import UnicodeWriter
from htmlentitydefs import name2codepoint 
pattern = re.compile(r'&(?:(#)(\d+)|([^;]+));')

output = open("merchant_category_information.csv", "wb")
UnicodeWriterObj = UnicodeWriter(output)
#csv_writer = csv.writer(output)
UnicodeWriterObj.writerow(['Updated On', 
                     'Merchant id',
                     'Merchant Name',
                     'averageConversionRate',
                     'averageCommission',
                     'logo',
                     'has_logo',
                     'category_id',
                     'category_name',
                     'domain_id',
                     'domain_name',
                     'country'])
for i in range(1, 624):
    info_pull_url = 'http://api-merchants.skimlinks.com/merchants/xml/639099dd7e85abb8717d17662901ecae/category/'+str(i)+'/limit/100000000'
    
    file = urllib2.urlopen(info_pull_url)
    data = file.read()
    file.close()
    dom = parseString(data)
    xmlTag = dom.getElementsByTagName('merchant')#[0].toxml()
    for merchant_xmlTag in xmlTag:
        #print merchant_xmlTag.toxml()
        updated_on = re.findall(r'dateUpdated>(.*?)</dateUpdated>', merchant_xmlTag.toxml())
        updated_on = ",".join(updated_on)
        merchant_id = re.findall(r'<merchantID>(.*?)</merchantID>', merchant_xmlTag.toxml())
        merchant_id = ",".join(merchant_id)
        merchant_name = re.findall(r'<merchantName>(.*?)</merchantName>', merchant_xmlTag.toxml())
        merchant_name = ",".join(merchant_name)
        averageConversionRate = re.findall(r'<averageConversionRate>(.*?)</averageConversionRate>', merchant_xmlTag.toxml())
        averageConversionRate = ",".join(averageConversionRate)
        averageCommission = re.findall(r'<averageCommission>(.*?)</averageCommission>', merchant_xmlTag.toxml())
        averageCommission = ",".join(averageCommission)
        logo = re.findall(r'<logo>(.*?)</logo>', merchant_xmlTag.toxml())
        logo = ",".join(logo)
        has_logo = re.findall(r'<has_logo>(.*?)</has_logo>', merchant_xmlTag.toxml())
        has_logo = ",".join(has_logo)
        category = re.findall(r'<category id="(.*?)">(.*?)</category>', merchant_xmlTag.toxml())[0]
        category_id = category[0]
        category_name = category[1].replace('&amp;', '&')
        domains = re.findall(r'<domainID>(.*?)</domainID>\s*<domainName>(.*?)</domainName>', merchant_xmlTag.toxml())[0]
        country = re.findall(r'<country>(.*?)</country>', merchant_xmlTag.toxml())
        country = ','.join(country)
        domain_id = domains[0]
        domain_name = domains[1]
#        print updated_on
#        print merchant_id
#        print merchant_name
#        print averageConversionRate
#        print averageCommission
#        print logo
#        print has_logo
#        print category_id
#        print category_name
#        print domain_id
#        print domain_name
#        print country
        UnicodeWriterObj.writerow([updated_on, merchant_id, merchant_name, averageConversionRate, averageCommission, logo, has_logo, category_id, category_name, domain_id, domain_name, country])
        print '*'*78
