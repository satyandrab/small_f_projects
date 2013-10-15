import urllib2
import re
from lxml import html
import csv
import mechanize
import cookielib

# Browser
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
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


data_writer = csv.writer(open("jobserve sample v1.1.csv", "wb"))
data_writer.writerow(['Job Title', 'Location', 'Rate/Salary', 'Description', 'Industry', 'Duration', 'Company', 'Contact', 'Email', 'Reference', 'Permalink'])



def main():
    url = 'http://www.jobserve.com/gb/en/JobListing.aspx?shid=AB7B24E79DDA4F1BA7&js=1'
    
#    html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    html_response = br.open(url)
    
    html_source = html_response.read()
    result = html_source.replace('\n', '').replace('\r', '')
    
    parsed_source = html.fromstring(result, url)
    parsed_source.make_links_absolute()
    
    get_urls = parsed_source.xpath("//a[@class='jobListPosition']/@href")
    for urls in get_urls:
        print urls
        get_details(urls)
        print '*'*78
    
def get_details(url):
    try:
    #    url = 'http://www.jobserve.com/gb/en/search-jobs-in-Buckinghamshire,-United-Kingdom/SYSTEMS-ENGINEER-MICROSOFT-VMWARE-CLOUD-BUCKINGHAMSHIRE-60K-116B476115E163A4/'
        
        #html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
        html_response = br.open(url)
        html_source = html_response.read()
        result = html_source.replace('\n', '').replace('\r', '')
        
        
        parsed_source = html.fromstring(result, url)
        parsed_source.make_links_absolute()
        
        title = parsed_source.xpath("//div[@id='td_jobpositionnolink']/text()")
        title = "".join(title)
        print title
        
        Location = parsed_source.xpath("//span[@id='md_location']/text()")
        Location = "".join(Location)
        print Location
        
        salary = parsed_source.xpath("//span[@id='md_rate']/text()")
        salary = "".join(salary)
        print salary
        
        desc = parsed_source.xpath("//div[@id='md_skills']/p/text()")
        desc = "".join(desc)
        print desc
        
        industry = parsed_source.xpath("//span[@id='md_industry']/a/text()")
        industry = "".join(industry)
        print industry
        
        duration = parsed_source.xpath("//span[@id='md_posted_date']/text()")
        duration = "".join(duration)
        print duration
        
        company = parsed_source.xpath("//span[@itemprop='name']/text()")
        company = "".join(company)
        print company
        
        contact = parsed_source.xpath("//span[@id='md_contact']/text()")
        contact = "".join(contact)
        print contact
        
        email = parsed_source.xpath("//span[@id='md_email']/a/@href['mailto']")
        email = "".join(email).replace('mailto:', '').split('?')[0]
        print email
        
        ref = parsed_source.xpath("//span[@id='md_ref']/text()")
        ref = "".join(ref)
        print ref
        
        Permalink = url
        print Permalink
        
        data_writer.writerow([title, Location, salary, desc, industry, duration, company, contact, email, ref, Permalink])
    except:
        pass
if __name__ == '__main__':
    main()