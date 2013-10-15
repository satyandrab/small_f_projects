import urllib2
import re
import csv

writer = csv.writer(open("silverpalaceinc v1.csv", "wb"))
writer.writerow(['url', 'Item number', 'Title','Image URL', 'Product Code','Product Type','Width', 'Metal', 'Finish', 'Description', 'Ring Size'])


def _get_details(url):
    data_list = []
    html_response = urllib2.urlopen(str(url))
    response = html_response.read().replace('\n','').replace('\r','')
    data_list.append(url)
    
    product_id = re.findall('Product Code:</span>: <span style="color:#DDDDDD;font-size:11px;font-weight:bold;">(.*?)</span>', response)
    product_code = "".join(product_id)
    data_list.append(product_code)
    
    temp_title = re.findall('<h1 class="productpageh1">(.*?)</h1>', response)
    title = "".join(temp_title)
    data_list.append(title)
    
    temp_img_url = re.findall('(http://www.silverpalaceinc.com/image/cache/data/.*?-1000x1000.jpg)', response)
    img_url = "".join(temp_img_url)
    data_list.append(img_url)
    
    data_list.append(product_code)
    
    temp_prod_type = re.findall('Product Type</span>: <span style="color:#DDDDDD;font-size:11px;font-weight:bold;">(.*?)</span>', response)
    prod_type = "".join(temp_prod_type)
    data_list.append(prod_type)
    
    temp_width = re.findall('Width</span>: <span style="color:#DDDDDD;font-size:11px;font-weight:bold;">(.*?)</span>', response)
    width = "".join(temp_width)
    data_list.append(width)
    
    temp_metal = re.findall('Metal</span>: <span style="color:#DDDDDD;font-size:11px;font-weight:bold;">(.*?)</span>', response)
    metal = "".join(temp_metal)
    data_list.append(metal)
    
    temp_finish = re.findall('Finish</span>: <span style="color:#DDDDDD;font-size:11px;font-weight:bold;">(.*?)</span>', response)
    finish = "".join(temp_finish)
    data_list.append(finish)
    
    temp_desc = re.findall('<div id="tab-description".*?>(.*?)</div>', response)
    desc = re.sub(r'<.*?>', '', "".join(temp_desc)).strip()
    data_list.append(desc)
    
    temp_size = re.findall('sizes of (.*?)\.', response)
    size = "".join(temp_size).replace('and ', '')
    data_list.append(size)
    
    writer.writerow(data_list)
    
def _get_prod_urls(url):
    html_response = urllib2.urlopen(str(url))
    response = html_response.read().replace('\n','').replace('\r','')
    
    cat_file = open('abc.htm', 'wb')
    cat_file.write(response)
    temp_prod_url = re.findall('<div class="name">.*?<a href="(http://www.silverpalaceinc.com/.*?)">', response)
    for prod_url in temp_prod_url:
        print prod_url
        _get_details(prod_url)
        print '*'*78
if __name__ == '__main__':
#    url = 'http://www.silverpalaceinc.com/wholesale-925-sterling-silver-316-stainless-steel-rhodium-brass-rings/wholesale-925-sterling-silver-animal-rings/Wholesale-Silver-Ring-CZ'
#    _get_details(url)
    cat_url = 'http://www.silverpalaceinc.com/wholesale-925-sterling-silver-316-stainless-steel-rhodium-brass-rings/wholesale-925-sterling-silver-toe-rings?limit=500'
    _get_prod_urls(cat_url)