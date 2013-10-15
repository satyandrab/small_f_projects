import urllib2
import re

import csv
output = open("serviceseeking.csv", "wb")
csv_writer = csv.writer(output)
csv_writer.writerow(["Category", "SubCategory", "Title", "Tel", "Addr", "Site", "ABN"])

def main():
#    url = 'http://www.serviceseeking.com.au/demolition/demolition/services/1'
#    get_all_landing_urls(url)
    url = 'http://www.serviceseeking.com.au/services'
    html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    
    find_cat = re.findall(r'<a href="/services/.*?/1">.*?</a><ul>.*?</ul>', html_response)
    for cat in find_cat:
        find_category = re.findall(r'<a href="/services/.*?/1">(.*?)</a><ul>', cat)
        print find_category
        if 'Sydney' in "".join(find_category):
            pass
        else:
            find_sub_category_url = re.findall(r'<li><a href="(/services/.*?/.*?/1)">(.*?)</a></li>', cat)
            if len(find_sub_category_url) > 0:
                for sub_cat_data in find_sub_category_url:
                    try:
                        sub_cat_url = 'http://www.serviceseeking.com.au'+sub_cat_data[0]
                        sub_cat_name = sub_cat_data[1]
                        find_category = "".join(find_category).replace('&amp;', '&')
                        sub_cat_name = sub_cat_name.replace('&amp;', '&')
                        print sub_cat_url
                        get_all_landing_urls(find_category, sub_cat_name, sub_cat_url)
                    except:
                        pass

def get_all_landing_urls(find_category, sub_cat_name, url):
    html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    
    find_all_landing_urls = re.findall(r'<a href="(/profile/.*?)" rel="canonical">.*?</a>', html_response)
    for landing_page_url in find_all_landing_urls:
        get_details(find_category, sub_cat_name, 'http://www.serviceseeking.com.au'+landing_page_url)

def get_details(category, subcategory, url):
#    url = 'http://www.serviceseeking.com.au/profile/25402-a-grade-tax'
    html_response = urllib2.urlopen(url).read().replace('\n', '').replace('\r', '')
    
    find_title = re.findall(r'<h1>(.*?)</h1>', html_response)
    find_title = "".join(find_title)
    print find_title
    
    find_tel = re.findall(r"<td class='muted'>tel</td><td class=.*?>(.*?)</td>", html_response)
    find_tel = "".join(find_tel)
    print find_tel
    
    find_addr = re.findall(r"<td class='muted'>addr</td><td .*?>(.*?)</td>", html_response)
    find_addr = re.sub(r'<.*?>', ' ', "".join(find_addr))
    find_addr = find_addr.strip()
    print find_addr
    
    find_site = re.findall(r"<td class='muted'>site</td><td .*?>(.*?)</td>", html_response)
    find_site = re.sub(r'<.*?>', ' ', "".join(find_site))
    find_site = find_site.strip()
    print find_site
    
    find_abn = re.findall(r"<td class='muted'>abn</td><td>(.*?)<", html_response)
    find_abn = "".join(find_abn)
    print find_abn
    
    csv_writer.writerow([category, subcategory, find_title, find_tel, find_addr, find_site, find_abn])
    
if __name__ == '__main__':
    main()