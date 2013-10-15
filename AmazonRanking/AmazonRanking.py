import mechanize_i
#from lxml_1 import html

import re
import csv

# Browser
br = mechanize_i.Browser()

# Cookie Jar
cj = mechanize_i._lwpcookiejar.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize_i._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
csv_file_name = 'Report.csv'
data_writer = csv.writer(open(csv_file_name, "wb"))
data_writer.writerow(['ASIN', 'Keyword', 'Rank', 'Results'])


def readtextfile():
    read_data_file = open('data.txt', 'rb')
    read_data_file.next()
    for line in read_data_file:
        line_splited = line.replace('\r\n','').split(',')
        ASIN = line_splited[0]#.lower()
        title = line_splited[1].lower()
        get_rank(ASIN, title)
    print "Done with all the keywords, Quitting  program......."
    
def get_rank(ASIN, title):
    try:
        rank = ''
        print "Searching Rank for '"+str(title)+"'"
        print '*'*78
        url = 'http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords='+str(title.replace(' ', '%20'))
        
        print url
        html_response = br.open(url)
        html_source = html_response.read()
        result = html_source.replace('\n', '').replace('\r', '')
        search_results = re.findall('Showing \d+ - \d+ of (.*?) Results', result)
        try:
            search_re = "".join(search_results[0])
        except:
            search_results = re.findall('<span>Showing (\d+) Results</span>', result)
            search_re = "".join(search_results[0])
        
        asin_list = re.findall('<div id="result_(\d+)" class=".*? prod celwidget" name="(.*?)">', result)
        res = dict((v,k) for k,v in dict(asin_list).iteritems())
        if ASIN in res.keys():
            print "ASIN found on page 1 with rank "+str(res[ASIN])
            rank = int(res[ASIN])+1
        else:
            url_page2 = 'http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords='+str(title.replace(' ', '%20'))+'&page=2'
            
            html_response = br.open(url_page2)
            html_source = html_response.read()
            result = html_source.replace('\n', '').replace('\r', '')
            
            asin_list_page_2 = re.findall('<div id="result_(\d+)" class=".*? prod celwidget" name="(.*?)">', result)
            res2 = dict((v,k) for k,v in dict(asin_list_page_2).iteritems())
            if ASIN in res2.keys():
                print "ASIN found on page 2 with rank "+str(res2[ASIN])
                rank = int(res2[ASIN])+1
            else:
                print "ASIN not found on page 1 or 2"
                rank = ''
        print "Updating CSV for Keyword '"+str(title)+"'"
    #    print (ASIN, title, rank, search_re)
        data_writer.writerow([ASIN, title, rank, search_re])
    except:
        pass

if __name__ == "__main__":
    readtextfile()