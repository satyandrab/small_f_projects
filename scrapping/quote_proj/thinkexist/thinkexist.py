import urllib2
import re

import csv
output = open("Sample_data_thinkexist.csv", "wb")
csv_writer = csv.writer(output)
csv_writer.writerow(["URL", "Bradcrumb", "Keyword", "Quote", "Author", "Rating"])


def main():
    url = 'http://en.thinkexist.com/quotes/with/keyword/azariah/'
    html_response1 = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    
    find_num_of_pages = re.findall(r'<font class="mf"> (\d+)</font>', html_response1)
    pages = "".join(find_num_of_pages)
    for i in range(1, (int(pages)/10)+2):
        page_url = url+str(i)+'.html'
        html_response = urllib2.urlopen(page_url).read().replace('\n', '').replace('\r', '')
    
        find_all_plate_div = re.findall(r'<div style="width: 100%">.*?</div>', html_response)
        
        find_keyword = re.findall(r'<h1>(.*?) quotes</h1>', html_response)
        find_keyword = "".join(find_keyword)
        
        find_category = re.findall(r'<a class="ob" href="/quotes/with/.*?">(.*?)</a>', html_response)
        find_category = " > ".join(find_category)
        
        for div_data in find_all_plate_div:
            quote = re.findall(r'<a class="sqq".*?>(.*?)</td>', div_data)
            quote = re.sub(r'<.*?>', '', "".join(quote))
            Author = re.findall(r'<a class="sqa" href=".*?">(.*?)</a>', div_data)
            Author = Author[0]
            rating = re.findall(r'<img height="7" width="39" src="/i/sq/(.*?)star.gif" alt="" />', div_data)
            rating = "".join(rating)
            print find_category
            print quote
            print Author
            print rating
            print find_keyword
            csv_writer.writerow([page_url, find_category, find_keyword, quote, Author, rating])
            print '*'*78

if __name__ == '__main__':
    main()